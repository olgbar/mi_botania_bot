import json
import logging
import re
from typing import Any, Dict, Optional, List 

from utils import text
from utils.ai import flash_model
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# -----------------------
# Funciones permitidas
# -----------------------
ALLOWED_FUNCTIONS = {
    "add_or_update_plant": {
        "description": "Registrar o actualizar una planta del usuario",
        "parameters": {
            "name": "string",
            "care": "string (opcional)",
            "water_every_days": "integer (opcional)"
        }
    },
    "remove_plant": {
        "description": "Eliminar una planta por nombre",
        "parameters": {
            "name": "string"
        }
    },
    "get_plants": {
        "description": "Listar plantas del usuario",
        "parameters": {}
    },
    "set_reminder": {
        "description": "Crear o actualizar un recordatorio",
        "parameters": {
            "plant_name": "string (opcional, se puede inferir de contexto)",
            "days_interval": "integer (REQUERIDO: número de días entre riegos, ej: 5, 7, 10)"
        }
    },
    "remove_reminder": {
        "description": "Eliminar un recordatorio por nombre",
        "parameters": {
            "plant_name": "string (opcional, puede usarse memoria)"
        }
    },
    "get_reminders": {
        "description": "Listar recordatorios activos",
        "parameters": {}
    },
    "analyze_text_issue": {
        "description": "Analizar síntomas y devolver diagnóstico",
        "parameters": {
            "text": "string"
        }
    }
}


# -----------------------
# MODEL Call
# -----------------------
def _call_model_for_function_call(user_text: str, user_id: int, current_plant: Optional[str] = None) -> str:
    """Llama al modelo con contexto de la planta actual"""

    system_prompt = (
        "Eres Botania, una asistente experta y amigable en plantas. Tu objetivo es ayudar al usuario a gestionar sus plantas y responder todas sus dudas botánicas.\n\n"
        
        "CONTEXTO Y ASUNCIONES:\n"
        f"- Última planta en contexto: {current_plant or 'ninguna'}.\n"
        "- Si la consulta sobre **cuidados/riego** no especifica una planta, asumí la última planta en contexto.\n"
        "- Si la solicitud de **añadir/eliminar planta o recordatorio** no especifica una planta, asumí la última planta en contexto.\n"
        "- **NO inventes nombres de plantas ni datos.**\n\n"
        
        "REGLAS DE FUNCIÓN Y ARGUMENTOS:\n"
        "- **add_or_update_plant:** Ejecutá esta función ante intenciones de 'añadir', 'agregar', 'guardar', 'registrar' o 'añadir X a mi lista'.\n"
        "- **remove_plant:** Ejecutá esta función ante intenciones de 'eliminar', 'borrar', 'quitar' o 'sacar' una planta.\n"
        "- **get_reminders:** Ejecutá esta función ante intenciones de 'ver', 'mostrar' o 'listar' recordatorios.\n"
        "- **set_reminder:**\n"
        "  1. Si falta el intervalo de días, DEBÉS preguntar al usuario: '¿Cada cuántos días?'\n"
        "  2. Si el usuario responde con un número o una frase con un número ('5', '7 días'), extrae el número entero para `days_interval`. Este parámetro DEBE ser `int`, NO `string`.\n\n"
        
        "FORMATO DE RESPUESTA ESTRICTO:\n"
        "**La respuesta de texto debe ser concisa (no mas de 150 palabras) y amigable.**\n"
        "- Utiliza etiquetas **HTML** (`<b>`, `<i>`) para formateo.\n"
        "- Utiliza `\n\n` para todos los saltos de línea y separación de párrafos.\n"
        "- **Tu ÚNICA respuesta debe ser un JSON, sin texto adicional:**\n"
        "  * **Para Función:** `{\"function_call\": {\"name\": \"FUNCION\", \"arguments\": {...}}}`\n"
        "  * **Para Texto:** `{\"response\": \"<HTML formatted text>\"}`\n\n"
        
        "Funciones disponibles:\n"
    )

    for fname, meta in ALLOWED_FUNCTIONS.items():
        system_prompt += f"- {fname}: {meta['description']}\n"

    user_prompt = f"Usuario ({user_id}) dijo: {user_text}"

    try:
        result = flash_model.models.generate_content(
            model="gemini-2.5-flash",
            contents=[system_prompt, user_prompt],
        )
        return result.text.strip()
    except Exception:
        logger.exception("Error llamando al modelo.")
        return json.dumps({
            "response": "<b>Ocurrió un problema procesando tu mensaje.</b>"
        })
    


# -----------------------
# Parse JSON
# -----------------------
def _safe_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """Extrae JSON de la respuesta del modelo"""
    text = text.strip()
    try:
        first = text.index('{')
        last = text.rfind('}')
        maybe = text[first:last+1]
        return json.loads(maybe)
    except:
        try:
            match = re.search(r'(\{.*\})', text, flags=re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except:
            logger.exception("Error parseando JSON.")
    return None

# -----------------------
# Detección inteligente de plantas con IA
# -----------------------
def _detect_plant_name(text: str, previous: Optional[str] = None) -> Optional[str]:
    """
    Usa Gemini para detectar nombres de plantas mencionadas en el texto.
    Incluye caché básico para evitar llamadas innecesarias.
    """
    text_lower = text.lower()
    #  Si la planta anterior se menciona explícitamente, mantenerla
    if previous and previous.lower() in text_lower:
        return previous
    
    # Filtro rápido: si no hay palabras clave de plantas, no llamar a la IA
    keywords = ['planta', 'hojas', 'regar', 'sol', 'sombra', 'tierra', 'maceta', 
                'un ', 'una ', 'mi ', 'la ', 'el ']
    if not any(kw in text_lower for kw in keywords):
        return None
    
    # Usar IA solo si pasó el filtro previo
    prompt = (
        "Analiza este mensaje y determina si menciona alguna planta específica.\n"
        "Si menciona una planta, responde SOLO con su nombre común en español (capitalizado).\n"
        "Si NO menciona ninguna planta específica, responde SOLO: NINGUNA\n"
        "Ejemplos:\n"
        "- 'Tengo un helecho' → Helecho\n"
        "- '¿Cómo riego las suculentas?' → Suculenta\n"
        "- 'Mi planta tiene hojas amarillas' → NINGUNA\n"
        "- 'La lavanda necesita sol?' → Lavanda\n\n"
        f"Mensaje del usuario: {text}"
    )
    
    try:
        result = flash_model.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        detected = result.text.strip()
        
        # Si la IA detectó algo válido
        if detected and detected != "NINGUNA" and len(detected) < 50:
            return detected
    except Exception as e:
        logger.warning(f"Error detectando planta con IA: {e}")
    
    return None


# -----------------------
# Ejecutores de funciones
# -----------------------
def _exec_add_or_update_plant(repo, user_id, args):
    name = args.get("name")
    care = args.get("care")
    days = args.get("water_every_days") or 7

    if not name:
        return "<b>Falta el nombre de la planta.</b>"

    try:
        days = int(days)
        repo.add_or_update_plant(user_id, name, care, days)

        # Guardar última planta mencionada
        repo.set_last_plant(user_id, name)

        return f"🌿 <b>{name}</b> guardada."
    except:
        logger.exception("Error en add/update plant")
        return "<b>No pude guardar la planta.</b>"


def _exec_remove_plant(repo, user_id, args):
    name = args.get("name")
    if not name:
        return "<b>Decime qué planta querés eliminar.</b>"
    try:
        repo.remove_plant(user_id, name)
        return f"🗑️ Eliminé <b>{name}</b> de tus plantas."
    except:
        logger.exception("Error remove plant")
        return "<b>No pude eliminar la planta.</b>"


def _exec_get_plants(repo, user_id, _args):
    try:
        plants = repo.get_plants(user_id)
        if not plants:
            return "No tenés plantas guardadas."
        html = "🌿<b>Tus plantas:</b><br><br>"
        for p in plants:
            html += f"• <b>{p['name']}</b><br><br>"
        return html
    except:
        logger.exception("Error get_plants")
        return "<b>No pude obtener las plantas.</b>"


def _exec_get_reminders(repo, user_id):
    try:
        rem = repo.get_reminders(user_id)
        if not rem:
            return "No tenés recordatorios activos."
        html = "<b>Recordatorios activos:</b><br><br>"
        for r in rem:
            html += f"• <b>{r['plant_name']}</b> — Cada {r['days_interval']} días<br><br>"
        return html
    except:
        logger.exception("Error get reminders")
        return "<b>No pude obtener los recordatorios.</b>"


def _exec_set_reminder(repo, reminders, user_id, args):
    plant_name = args.get("plant_name")
    days = args.get("days_interval")

    if days is None:
        return "<b>Indicá cada cuántos días querés el recordatorio.</b>"
    days = int(days)

    # Usar memoria si no hay planta explícita
    if not plant_name:
        plant_name = repo.get_last_plant(user_id)
        if not plant_name:
            return "Decime qué planta querés recordar."

    # Guardar contexto
    repo.set_last_plant(user_id, plant_name)

    try:
        repo.set_reminder(user_id, plant_name, days)
        if reminders:
            reminders.schedule_plant(user_id, plant_name, days)
        return f"⏰ Recordatorio creado para <b>{plant_name}</b> cada {days} días."
    except:
        logger.exception("Error set reminder")
        return "<b>No pude crear el recordatorio.</b>"


def _exec_remove_reminder(repo, reminders, user_id, args):
    plant_name = args.get("plant_name")

    # Usar memoria si no hay nombre explícito
    if not plant_name:
        plant_name = repo.get_last_plant(user_id)
        if not plant_name:
            return "Decime qué recordatorio querés eliminar."

    plant_name_normalized = plant_name.strip().lower()
    try:
        if reminders:
            reminders.remove_plant_reminder(user_id, plant_name_normalized)
        repo.remove_reminder(user_id, plant_name_normalized)
        repo.set_last_plant(user_id, '')
        return f"🗑 Eliminé el recordatorio de <b>{plant_name}</b>."
    except:
        logger.exception("Error remove reminder")
        return "<b>No pude eliminar el recordatorio.</b>"


def _exec_analyze_text_issue(repo, user_id, args):
    text = args.get("issue") or args.get("text") or args.get("issue_description") or args.get("symptoms") or ""
    if not text:
        return "<b>No entendí el problema de la planta.</b>"

    prompt = (
        "Analiza este problema de planta y responde en HTML simple (sin <html>, <body> ni estilos CSS). "
        "Usa solo <b>negrita</b>, <i>cursiva</i> y saltos de línea. "
        "Máximo 120 palabras:\n"
        f"{text}"
    )

    try:
        result = flash_model.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return result.text.strip()

    except:
        logger.exception("Error analyzing issue")
        return "<b>No pude analizar el problema.</b>"

# -----------------------
# Router principal
# -----------------------
def process_user_message(user_text: str, user_id: int, repo, reminders=None) -> str:
    
    """
    Procesa el mensaje del usuario y ejecuta la función correspondiente.
    """
    
    current_plant = repo.get_last_plant(user_id)

    # DEBUG CONTEXTUAL
    print(f"🔍 [CONTEXTO] Planta actual: {current_plant}")
    print(f"🔍 [CONTEXTO] Mensaje: {user_text}")

    # Detectar si hay una nueva planta mencionada
    detected = _detect_plant_name(user_text, current_plant)
    if detected and detected != current_plant:
        repo.set_last_plant(user_id, detected)
        current_plant = detected
        print(f"🔍 [CONTEXTO] Nueva planta detectada: {detected}")

    # Llamar al modelo con el contexto actualizado
    raw = _call_model_for_function_call(user_text, user_id, current_plant)
    print(f"🤖 [DEBUG] Raw IA: {raw}")

    # Parsear respuesta
    parsed = _safe_parse_json(raw)
    print(f"📦 [DEBUG] Parsed: {parsed}")
    
    if not parsed:
        return "<b>No entendí tu mensaje.</b>"

    # Ejecutar función si corresponde
    if "function_call" in parsed:
        fc = parsed["function_call"]
        name = fc.get("name")
        args = fc.get("arguments", {})
        print(f"🔍 [DEBUG] Función: {name}, Argumentos: {args}")
        
        # Inyectar contexto si falta el nombre
        if name == "add_or_update_plant" and not args.get("name"):
            if current_plant:
                args["name"] = current_plant

        # Memoria para recordatorios si el modelo no envió plant_name
        if name in ("set_reminder", "remove_reminder") and not args.get("plant_name"):
            if current_plant:
                args["plant_name"] = current_plant

        # Ejecutar función
        if name == "add_or_update_plant":
            return _exec_add_or_update_plant(repo, user_id, args)
        
        if name == "remove_plant":
            return _exec_remove_plant(repo, user_id, args)

        if name == "get_plants":
            return _exec_get_plants(repo, user_id, args)

        if name == "get_reminders":
            return _exec_get_reminders(repo, user_id)

        if name == "set_reminder":
            return _exec_set_reminder(repo, reminders, user_id, args)

        if name == "remove_reminder":
            return _exec_remove_reminder(repo, reminders, user_id, args)

        if name == "analyze_text_issue":
            return _exec_analyze_text_issue(repo, user_id, args)

        return "<b>No pude ejecutar la acción solicitada.</b>"

    # Respuesta directa del modelo
    if "response" in parsed:

        raw_response = parsed["response"]
        clean_response = text.html_a_markdown(raw_response)
        # Intentar detectar planta mencionada en el mensaje original
        if not current_plant:
            detected_late = _detect_plant_name(user_text, None)
            if detected_late:
                repo.set_last_plant(user_id, detected_late)
                print(f"[CONTEXTO] Planta detectada tardíamente: {detected_late}")
        
        return clean_response  # Retornar la respuesta

    return "<b>No entendí tu mensaje.</b>"
