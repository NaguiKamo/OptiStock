from django.urls import path
from . import views


app_name = 'inventario'
urlpatterns = [
    path('', views.lista_productos, name='inicio'),
    path('productos/', views.lista_productos, name='lista_productos'),
    
    path('almacenes/', views.lista_almacenes, name='lista_almacenes'),    
    path('reportes/', views.panel_reportes, name='panel_reportes'),      
    
  
    path('categorias/', views.lista_categorias, name='lista_categorias'),
  
    #path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),

    path('productos/crear/', views.crear_producto, name='crear_producto'),

    #path('productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
]