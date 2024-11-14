from django.shortcuts import render

# Create your views here.
from django.template.loader import render_to_string

# Define your context data
context = {
    'edition': 'value1',
    'key2': 'value2',
}

# Render the template with the context
html = render_to_string('template_name.html', context)
print(html)