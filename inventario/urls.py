from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('productos/', views.lista_productos, name='lista_productos'),
    
    path('almacenes/', views.lista_almacenes, name='lista_almacenes'),    
    path('reportes/', views.panel_reportes, name='panel_reportes'),      
    
    # Acciones de productos
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),

    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
]