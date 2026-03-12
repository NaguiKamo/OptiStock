from django.contrib import admin
from .models import Producto,Categorias,Almacen,Inventario,Movimiento

# Register your models here.

admin.site.register(Categorias)
admin.site.register(Producto)
admin.site.register(Almacen)
admin.site.register(Inventario)
admin.site.register(Movimiento)