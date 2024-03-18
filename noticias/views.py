from django.shortcuts import render, redirect, get_object_or_404
from .models import Noticia, Fuente
from django.views.generic import ListView
from .scrapers import scrape_ukrinform, scrape_bbc, scrape_cnn, scrape_onu
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models import Count
from django.contrib.auth.decorators import login_required

# Create your views here.

def welcome(request):
    return render(request, 'welcome.html')

# Definición de una vista basada en clase para mostrar los resultados del filtro
class ResultadosFiltro(ListView):
    model = Noticia
    template_name = 'resultados_filtro.html'
    context_object_name = 'noticias'
    
    # Método para agregar datos adicionales al contexto
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fuentes_seleccionadas = set(self.request.GET.getlist('fuente'))
        context['fuentes_seleccionadas'] = fuentes_seleccionadas
        return context

    # Método para obtener el conjunto de consultas filtradas
    def get_queryset(self):
        fuentes_seleccionadas = self.request.GET.getlist('fuente')
        queryset = Noticia.objects.filter(publicada=True)  # Solo noticias publicadas
        
        if fuentes_seleccionadas:
            query = Q()
            for fuente in fuentes_seleccionadas:
                query |= Q(fuente__nfuente=fuente)
            queryset = queryset.filter(query)
            
        # Ordenar las noticias por fecha de extracción
        queryset = queryset.order_by('-fextraccion')
        
        # Anotar el recuento de noticias publicadas
        queryset = queryset.annotate(publicada_count=Count('publicada', filter=Q(publicada=True)))
        
        return queryset
    
# Definición de una vista basada en clase para mostrar los resultados de la búsqueda por palabra clave
class ResultadoBusqueda(ListView):
    model = Noticia
    template_name = 'resultados_palabra_clave.html'
    context_object_name = 'noticias'

    # Método para obtener el conjunto de consultas filtradas por palabra clave
    def get_queryset(self):
        queryset = Noticia.objects.filter(publicada=True)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(titular__icontains=query) | queryset.filter(contenido__icontains=query)
        # Ordenar las noticias por fecha de extracción
        queryset = queryset.order_by('-fextraccion')
        return queryset

    # Método para agregar datos adicionales al contexto
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = str(self.request.GET.get('q', ''))
        context['query'] = query
        return context

# Definición de una vista para la página de inicio
def home(request):
    # Obtener todas las noticias ordenadas por fecha de extracción
    noticias = Noticia.objects.filter(publicada=True).order_by('-fextraccion')
    
    # Paginar las noticias
    paginator = Paginator(noticias, 5)  # Mostrar 5 noticias por página
    page = request.GET.get('page')
    try:
        noticias_paginadas = paginator.page(page)
    except PageNotAnInteger:
        # Si el parámetro de la página no es un número, mostrar la primera página
        noticias_paginadas = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango (por encima del número máximo de páginas), mostrar la última página
        noticias_paginadas = paginator.page(paginator.num_pages)

    return render(request, 'home.html', {'noticias_publicadas': noticias_paginadas})

# Definición de una vista para la página de contexto histórico
def historiccontext(request):
    return render(request, 'historic_context.html')

# Definición de una vista para iniciar el proceso de raspado de noticias
def scrape_noticias(request):
    # Lógica para llamar a los scrapers y almacenar las noticias en la base de datos
    scrape_ukrinform()
    scrape_bbc()
    scrape_cnn()
    scrape_onu()
    # Redirecciona a la página de administrador
    return redirect('noticias:administrator')

# Definición de una vista para la página de administrador
@login_required(login_url='noticias:home')
def administrator(request):
    if request.method == 'POST':
        noticia_id = request.POST.get('noticia_id')
        if noticia_id:
            noticia = get_object_or_404(Noticia, id=noticia_id)
            if 'publicar' in request.POST:
                noticia.publicada = True # Marca la noticia como en la página de inicio al publicar
            elif 'despublicar' in request.POST:
                noticia.publicada = False
                noticia.enhome = False  # Desmarca la noticia de la página de inicio al despublicar
            noticia.save()
            return redirect('noticias:administrator')

    # Obtener todas las noticias ordenadas por fecha de extracción
    noticias = Noticia.objects.all().order_by('-fextraccion')

    return render(request, 'administrator.html', {'noticias': noticias})

# Definición de una vista para mostrar el detalle de una noticia específica
def noticia_detail(request, noticia_id):
    # Obtener la noticia específica según su ID
    noticia = get_object_or_404(Noticia, pk=noticia_id)
    return render(request, 'noticia_detail.html', {'noticia': noticia})

# Definición de una vista para cerrar sesión
def logout_view(request):
    return render(request, 'logout.html')