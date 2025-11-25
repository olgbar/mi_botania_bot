"""
Constantes centralizadas para evitar duplicación
Creado para eliminar strings repetidos en múltiples archivos
"""

class Messages:
    """Mensajes de respuesta del bot"""
    
    # ============ ERRORES GENÉRICOS ============
    ERROR_GENERIC = "<b>Ocurrió un error procesando tu mensaje.</b>"
    ERROR_CONNECTION = "Disculpa, tengo un problema de conexión con mis servidores. Por favor, intenta tu consulta más tarde. 🥺"
    ERROR_API = "<b>Ocurrió un problema procesando tu mensaje.</b>"
    
    # ============ PLANTAS ============
    PLANT_NOT_FOUND = "<b>No encontré esa planta.</b>"
    PLANT_SAVED = "🌿 <b>{name}</b> guardada."
    PLANT_REMOVED = "🗑 Eliminé <b>{name}</b> de tus plantas."
    PLANT_MISSING_NAME = "<b>Falta el nombre de la planta.</b>"
    NO_PLANTS = "No tenés plantas registradas."
    ASK_PLANT_TO_DELETE = "Decime qué planta querés eliminar."
    ASK_PLANT_FOR_REMINDER = "Decime el nombre de la planta para recordar."
    
    # ============ RECORDATORIOS ============
    REMINDER_CREATED = "⏰ Recordatorio creado para <b>{plant_name}</b> cada {days} días."
    REMINDER_REMOVED = "🗑 Eliminé el recordatorio de <b>{plant_name}</b>."
    REMINDER_NOT_FOUND = "No encontré ese recordatorio."
    NO_REMINDERS = "No tenés recordatorios activos."
    ASK_REMINDER_INTERVAL = "¿Cada cuántos días querés que te recuerde?"
    REMINDER_INVALID_DAYS = "<b>Indicá cada cuántos días querés el recordatorio.</b>"
    REMINDER_INVALID_NUMBER = "<b>Número inválido. Por favor, ingresá solo el número de días.</b>"
    REMINDER_OUT_OF_RANGE = "<b>Por favor, ingresá un número entre 1 y 365 días.</b>"
    
    # ============ IDENTIFICACIÓN ============
    PLANT_UNKNOWN = "Planta Desconocida (Error en la identificación)"
    CARE_DEFAULT = "No pude contactar a la IA para analizar la foto. Revisa la terminal para más detalles."
    ANALYZING_IMAGE = "🔍 Analizando tu planta..."
    IMAGE_ERROR = "❌ Error procesando la imagen. Por favor, intenta de nuevo."


class DetectionConfig:
    """Configuración para detección de plantas"""
    
    #Keywords optimizadas (sin falsos positivos como "un", "una")
    PLANT_KEYWORDS = [
        'planta', 'plantas',
        'hojas', 'hoja',
        'regar', 'riego', 'riega',
        'sol', 'luz', 'sombra',
        'tierra', 'sustrato', 'suelo',
        'maceta', 'macetas',
        'cultivar', 'cultivo',
        'sembrar', 'siembra',
        'trasplantar', 'trasplante',
        'verde', 'verdes',
        'flor', 'flores',
        'raíz', 'raíces',
        'fertilizante', 'abono'
    ]
    
    MAX_PLANT_NAME_LENGTH = 50


class APIConfig:
    """Configuración de límites de API"""
    
    MAX_TOKENS = 1000
    TIMEOUT_SECONDS = 30
    MAX_RETRIES = 3  # Número de reintentos en caso de fallo
    RETRY_DELAY = 2  # Segundos entre reintentos