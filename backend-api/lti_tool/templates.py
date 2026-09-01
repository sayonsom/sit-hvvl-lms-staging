import os
import re

def render_template(template_name, context):
    """
    Render the HTML content based on the template and context.
    """
    template_path = os.path.join('templates', template_name)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        # Replace placeholders {{ key }} with context values
        for key, value in context.items():
            if isinstance(value, list):
                value = ', '.join(value)
            elif isinstance(value, dict):
                continue  # Skip dictionaries or handle as needed
            placeholder_pattern = r'{{\s*' + re.escape(key) + r'\s*}}'
            template_content = re.sub(placeholder_pattern, str(value), template_content)
        # Remove any unreplaced placeholders
        template_content = re.sub(r'{{\s*\w+\s*}}', '', template_content)
        return template_content
    except FileNotFoundError:
        return "<html><body><h1>Template not found</h1></body></html>"