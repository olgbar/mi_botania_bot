import re
import google.genai as gen 
from google.genai.types import Part
from config import GEMINI_API_KEY

client = gen.Client(api_key=GEMINI_API_KEY)

flash_model = client

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
        
    try:
        print("Analizando imagen con el modelo Gemini...")
        
        # ===================================================
        # Crear Part en memoria
        # ===================================================
        image_part = Part.from_bytes(
            data=image_bytes, 
            mime_type='image/jpeg'
        )

        # Generar el contenido (client.models)
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
