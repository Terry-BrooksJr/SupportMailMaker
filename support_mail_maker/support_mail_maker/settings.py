import django
from django.conf import settings

settings.configure(
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['path/to/your/templates'],  # Specify the directory containing your templates
            'APP_DIRS': False,
            'OPTIONS': {
                'context_processors': [],  # Add context processors if needed
            },
        },
    ]
)
django.setup()