import re
import google.genai as gen 
from google.genai.types import Part
from config import GEMINI_API_KEY

client = gen.Client(api_key=GEMINI_API_KEY)

flash_model = client

# ---------------------------------------
# Chat fluido
# ---------------------------------------
def chat_with_ai(text):
    prompt = (
        f"Te llamas Botania y debes responder como una experta en plantas."
        f"Evita sonar académica o distante: tu objetivo es que cualquier persona disfrute aprendiendo sobre plantas y se sienta acompañada en su curiosidad."        
        f"Mantené la respuesta concisa y con un máximo de 3000 caracteres."
        f"Divide la respuesta en párrafos lógicos. Utiliza sólo etiquetas HTML para: "
        f"<b> cuando requieras negrita, <i> cuando requieras cursiva."
        f"Si querés usar listas, hacelo con guiones o puntos, ej: • item"
        f"Respondé a la siguiente consulta:  {text}"
    )
    #el límite deTelegram es 4096 caracteres 
    try:
        respuesta = flash_model.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return respuesta.text
    except Exception as e:
        print(f"Error en chat_with_ai: {e}")
        return "Disculpa, tengo un problema de conexión con mis servidores. Por favor, intenta tu consulta más tarde. 🥺"

def identify_plant(image_bytes):
    prompt = (
        "Eres un experto en botánica. Analiza la imagen proporcionada."
        "Responde **SOLO** con el siguiente formato, sin explicaciones ni texto introductorio:"
        "Nombre: [Nombre Común de la Planta]"
        "Riego: [Número de días, ej: 7] días"
        "Cuidados: [Cuidados detallados y concisos, no más de 50 palabras.]"
    )
    
    default_result = {
        "nombre": "Planta Desconocida (Error en la identificación)",
        "riego": 7,
        "cuidados": "No pude contactar a la IA para analizar la foto. Revisa la terminal para más detalles."
    }
    
    # Inicialización de variables para evitar errores de Pylance
    nombre = default_result["nombre"]
    riego = default_result["riego"]
    cuidados = default_result["cuidados"]
    
    # El objeto Part.from_bytes necesita el import 'from google.genai.types import Part'
    
    try:
        print("Analizando imagen con el modelo Gemini...")
        
        # ===================================================
        # Crear Part en memoria
        # ===================================================
        image_part = Part.from_bytes(
            data=image_bytes, 
            mime_type='image/jpeg'
        )

        # PASO 2: Generar el contenido (client.models)
        result = flash_model.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image_part],
            # config=GenerateContentConfig(timeout=90)
        )
        texto = result.text.strip()

        # ===================================================
        # Lógica de Parseo (Extracción de datos)
        # ===================================================
        
        for line in texto.split('\n'):
            line_lower = line.lower().strip()
            
            if line_lower.startswith("nombre:"):
                nombre = line.split(':', 1)[1].strip()
                
            elif line_lower.startswith("riego:"):
                match = re.search(r'(\d+)', line_lower)
                if match:
                    riego = int(match.group(1))
                    
            elif line_lower.startswith("cuidados:"):
                cuidados = line.split(':', 1)[1].strip()

        if not (1 <= riego <= 30):
            riego = 7

        # Retornar el resultado exitoso
        return {
            "nombre": nombre,
            "riego": riego,
            "cuidados": cuidados
        }


    except Exception as e:
        print("=========================================================")
        print(f"FALLO CRÍTICO DE LA API DE GEMINI: {e}")
        print("=========================================================")
        return default_result
