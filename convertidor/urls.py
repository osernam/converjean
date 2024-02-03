from django.urls import path, re_path
from . import views

app_name = "convertidor"

urlpatterns = [
    path('', views.homeView, name='home'),
    path('res1/', views.res1, name='res1'),
    path('res2/', views.res2, name='res2'),
    path('cargar/', views.resumen, name='cargar_archivo_excel'),
    path('descargarJeansFinal/', views.resultadosJeansFinal, name='resultadosJeansFinal'),
    
    
    #re_path(r'^.*/$', redireccionar_a_inicio),
]