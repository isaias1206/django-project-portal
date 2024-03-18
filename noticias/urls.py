from django.urls import path
from . import views
from .views import ResultadosFiltro, ResultadoBusqueda

app_name = 'noticias'

urlpatterns = [
        path('welcome/', views.welcome, name='welcome'),
        path('home/', views.home, name='home'),
        path('administrator/', views.administrator, name='administrator'),
        path('historiccontext/', views.historiccontext, name='historiccontext'),
        path('scrape-noticias/', views.scrape_noticias, name='scrape_noticias'),
        path('noticia/<int:noticia_id>/', views.noticia_detail, name='noticia_detail'),
        path('resultados-filtro/', ResultadosFiltro.as_view(), name='resultados_filtro'),
        path('resultados-palabra-clave/', ResultadoBusqueda.as_view(), name='resultados_palabra_clave'),
        path('logout/', views.logout_view, name='logout'),
] 