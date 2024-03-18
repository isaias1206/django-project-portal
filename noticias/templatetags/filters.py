import re  # Importar el módulo de expresiones regulares
from django import template  # Importar el módulo de plantillas de Django
from django.utils.html import mark_safe  # Importar la función mark_safe para marcar el texto seguro para la salida HTML

register = template.Library()  # Registrar una nueva etiqueta o filtro en el sistema de plantillas de Django

@register.filter  # Decorador para registrar la función como un filtro en las plantillas de Django
def highlight(text, keyword):
    # Escapar los caracteres especiales en la palabra clave para evitar errores en la expresión regular
    keyword_escaped = re.escape(keyword)
    # Realizar la sustitución utilizando una expresión regular para resaltar la palabra clave en el texto
    highlighted_text = re.sub(r'\b' + keyword_escaped + r'\b', r'<span class="highlight">\g<0></span>', text, flags=re.IGNORECASE)
    return mark_safe(highlighted_text)  # Marcar el texto seguro para la salida HTML usando mark_safe para evitar la escapada automática del texto en la plantilla