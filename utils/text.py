import re
import html2text

def html_a_markdown(texto_html: str) -> str:
    h = html2text.HTML2Text()
    
    # ---Configuración para evitar el 'wrapping' y asegurar bloques
    h.ignore_links = True
    h.ignore_images = True
    h.body_width = 0            # CRÍTICO: Deshabilita el ajuste de línea
    h.single_line_break = False 
    h.p_p_string = "\n\n"       # Separador de párrafos
    
    # --- Configuración de Listas
    h.ul_item_mark = '• '
    # CORRECCIÓN CLAVE: Fuerza un salto de línea después de cada bullet.
    h.list_item_separator = "\n" 
    
    # ---- Configuración de Estilo
    # Asegura que <b> se convierta a ** (negrita en Markdown)
    h.use_telegram_style = True
    
    # Procesa y limpia el resultado
    markdown_text = h.handle(texto_html).strip()
    
    # Limpieza final: reduce saltos de línea excesivos
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
    
    return markdown_text

# def limpiar_html_telegram(texto):
#     """
#     Limpia y transforma HTML generado por la IA para que sea compatible con Telegram.
#     """

#     # --- 1) Eliminar DOCTYPE y estructuras HTML completas ---
#     texto = re.sub(r'<!DOCTYPE[^>]*>', '', texto, flags=re.IGNORECASE)
#     texto = re.sub(r'</?(html|head|body|meta|script|style|title)[^>]*>', '', texto, flags=re.IGNORECASE)

#     # --- 2) Reemplazos estructurales ---
#     reemplazos = [
#         (r'<br\s*/?>', '\n\n'),
#         (r'</?(div|section|article|header|footer)[^>]*>', '\n\n'),
#         (r'</?p[^>]*>', '\n\n'),
#         (r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'\n\n<b>\1</b>\n\n'),
#         # Mantener el patrón de encabezados con saltos
#         (r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'\n\n<b>\1</b>\n\n')
#     ]
#     for patron, reemplazo in reemplazos:
#         texto = re.sub(patron, reemplazo, texto, flags=re.IGNORECASE | re.DOTALL)

#     # --- 3) Listas ul/li → bullets ---
#     texto = re.sub(r'<ul[^>]*>', '', texto)
#     texto = re.sub(r'</ul>', '', texto)
#     texto = re.sub(r'<li[^>]*>', '• ', texto)
#     texto = re.sub(r'</li>', '\n', texto)

#     # --- 4) Eliminar etiquetas no permitidas ---
#     texto = re.sub(r'</?(span|svg|img|video|figure|table|tr|td|th|tbody|thead)[^>]*>', '', texto)

#     # --- 5) Mantener solo atributos válidos en etiquetas permitidas ---
#     texto = re.sub(r'<(b|i|u|s|a|code|pre)[^>]*>', r'<\1>', texto)

#     # --- 6) Limpieza final ---
#     texto = re.sub(r'\n{3,}', '\n\n', texto)
#     texto = texto.strip()

#     return texto
