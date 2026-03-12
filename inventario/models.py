from django.db import models

# Create your models here.
class Categorias(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)


class Producto(models.Model):
    categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE, null= True)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=100)
    precio_compra = models.DecimalField(max_digits=10,decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo= models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)


class Almacen(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre
    

class Inventario (models.Model):
    producto = models.ForeignKey(Producto, on_delete= models.CASCADE )
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, null=True)
    cantidad = models.IntegerField(default=0)

    class Meta:
        unique_together = ('producto','almacen')

    def __str__(self):
        return f"{self.producto.nombre} - {self.almacen.nombre}"

class Movimiento(models.Model):
    TIPOS = (
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=255, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.Producto.nombre}"
