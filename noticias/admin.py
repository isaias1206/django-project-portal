from django.contrib import admin
from .models import Noticia, Fuente

# Register your models here.

admin.site.site_header = 'Panel Administrativo | Mundo Pugna'
admin.site.register(Noticia)