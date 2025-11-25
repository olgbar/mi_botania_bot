import re

def html_a_markdown(html):
    if not html:
        return ""

    # Reemplazos básicos
    html = html.replace("<b>", "**").replace("</b>", "**")
    html = html.replace("<strong>", "**").replace("</strong>", "**")
    html = html.replace("<i>", "_").replace("</i>", "_")
    html = html.replace("<em>", "_").replace("</em>", "_")
    html = html.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")

    # Quitar cualquier tag HTML restante
    html = re.sub(r"<.*?>", "", html)

    return html.strip()
