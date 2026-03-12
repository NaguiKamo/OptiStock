from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import csv
from .models import Producto, Categorias, Inventario, Movimiento
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, F , ExpressionWrapper, DecimalField



# Create your views here.
# VISTA DE PRODUCTOS (CRUD)
def lista_productos(request):
    productos = Producto.objects.all().order_by('nombre')
    categorias = Categorias.objects.all().order_by('nombre')
    # Definimos active_page para que el menú lateral sepa qué opción resaltar
    return render(request, 'inventario/productos.html', {
        'productos': productos,
        'categorias': categorias,
        'active_page': 'productos'
    })

# Vista para manejar la creación de producto (POST)
def crear_producto(request):
    if request.method == 'POST':
        # Capturamos datos del formulario POST
        cat_id = request.POST.get('categoria')
        categoria = Categorias.objects.get(id=cat_id) if cat_id else None
        
        # Obtenemos el estado del checkbox (si no está, es False)
        activo = True if request.POST.get('activo') else False
        
        Producto.objects.create(
            nombre=request.POST.get('nombre'),
            codigo=request.POST.get('codigo'),
            descripcion=request.POST.get('descripcion'),
            precio_compra=request.POST.get('precio_compra'),
            precio_venta=request.POST.get('precio_venta'),
            stock_minimo=request.POST.get('stock_minimo'),
            categoria=categoria,
            activo=activo
        )
    return redirect('lista_productos')

# Vista para eliminar producto
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('lista_productos')

# (Faltaría implementar editar_producto, similar a crear pero con .save())


# VISTA DE REPORTES (Cálculos avanzados)
def panel_reportes(request):
    now = timezone.now()
    periodo = request.GET.get('periodo', 'month') # Por defecto: este mes
    
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    label = "Hoy"

    # 1. Definir rango de tiempo para los filtros
    if periodo == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        label = "Hoy"
    elif periodo == 'week':
        start_date = now - timedelta(days=now.weekday()) # Lunes de esta semana
        label = "Esta Semana"
    elif periodo == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0) # 1º de este mes
        label = "Este Mes"
    elif periodo == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0) # 1º de Enero
        label = "Este Año"
    elif periodo == 'all':
        start_date = now.replace(year=2000) # Una fecha muy vieja
        label = "Todo el histórico"

    # 2. Cálculos de Movimientos en el periodo
    movimientos_periodo = Movimiento.objects.filter(fecha__gte=start_date).order_by('-fecha')
    total_movs = movimientos_periodo.count()
    entradas = movimientos_periodo.filter(tipo='ENTRADA').count()
    salidas = movimientos_periodo.filter(tipo='SALIDA').count()

    # 3. Cálculos de Stock actual (Independiente del periodo de tiempo)
    # Obtenemos solo los registros de Inventario donde cantidad > 0
    stock_actual = Inventario.objects.filter(cantidad__gt=0)
    total_prods_stock = stock_actual.count()
    
    # -- Sumatoria precio de venta por producto --
    # Usamos agregación ORM para calcular cantidad * precio_venta para cada fila y sumarlos
    valor_total_venta = stock_actual.aggregate(
        total=Sum(F('cantidad') * F('producto__precio_venta'), output_field=DecimalField())
    )['total'] or 0

    # -- Diferencia entre precio de venta y precio de compra --
    # Calculamos (Venta - Compra) * cantidad para cada registro de stock
    ganancia_proyectada = stock_actual.aggregate(
        total_margen=Sum(
            ExpressionWrapper(
                (F('producto__precio_venta') - F('producto__precio_compra')) * F('cantidad'),
                output_field=DecimalField()
            )
        )
    )['total_margen'] or 0

    return render(request, 'inventario/reportes.html', {
        'active_page': 'reportes',
        'periodo_actual': periodo,
        'periodo_actual_label': label,
        'movimientos_periodo': movimientos_periodo[:10], # Mostramos solo últimos 10
        'total_movimientos': total_movs,
        'entradas': entradas,
        'salidas': salidas,
        'total_productos_stock': total_prods_stock,
        'total_valor_venta': valor_total_venta,
        'total_ganancia_proyectada': ganancia_proyectada,
    })

def lista_categorias(request):
    # Si el usuario envía el formulario
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        
        Categorias.objects.create(
            nombre=nombre,
            descripsion=descripcion # Ojo: asegúrate de que se llame así en tu modelo
        )
        return redirect('lista_categorias')

    # Para mostrar la tabla
    todas_categorias = Categorias.objects.all()
    return render(request, 'inventario/categorias.html', {
        'categorias': todas_categorias,
        'active_page': 'categorias'
    })

def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categorias, id=id)
    categoria.delete()
    return redirect('lista_categorias')

def lista_almacenes(request):
    return render(request, 'inventario/almacen.html', {'active_page': 'almacen'})