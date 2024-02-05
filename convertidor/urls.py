from django.urls import path, re_path
from . import views

app_name = "convertidor"

urlpatterns = [
    path('', views.homeView, name='home'),
    path('res1/', views.res1, name='res1'),
    path('res2/', views.res2, name='res2'),
    path('res3/', views.res3, name='res3'),
    
    
    
    #re_path(r'^.*/$', redireccionar_a_inicio),
]