from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categorias, Inventario, Movimiento 
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages


@login_required
def lista_productos(request):
    productos = Producto.objects.all().order_by('nombre')
    categorias = Categorias.objects.all() 
    
    return render(request, 'inventario/productos.html', {
        'productos': productos,
        'categorias': categorias,
        'active_page': 'productos'
    })
    
@login_required
def crear_producto(request):
    if request.method == 'POST':
        cat_id = request.POST.get('categoria')
        categoria = Categorias.objects.get(id=cat_id) if cat_id else None
        
        activo = True if request.POST.get('activo') else False
        
       
        Producto.objects.create(
            nombre=request.POST.get('nombre'),
            codigo=request.POST.get('codigo'),
            descripcion=request.POST.get('descripcion'),
            precio_compra=request.POST.get('precio_compra') or 0,
            precio_venta=request.POST.get('precio_venta') or 0,
            stock_minimo=request.POST.get('stock_minimo') or 0,
            categoria=categoria,
            activo=activo
        )
        return redirect('inventario:lista_productos')

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('inventario:lista_productos')

@login_required
def panel_reportes(request):
    now = timezone.now()
    periodo = request.GET.get('periodo', 'month')
    
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    label = "Hoy"

    if periodo == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        label = "Hoy"
    elif periodo == 'week':
        start_date = now - timedelta(days=now.weekday())
        label = "Esta Semana"
    elif periodo == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0)
        label = "Este Mes"
    elif periodo == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0)
        label = "Este Año"
    elif periodo == 'all':
        start_date = now.replace(year=2000)
        label = "Todo el histórico"

    movimientos_periodo = Movimiento.objects.filter(fecha__gte=start_date).order_by('-fecha')
    total_movs = movimientos_periodo.count()
    entradas = movimientos_periodo.filter(tipo='ENTRADA').count()
    salidas = movimientos_periodo.filter(tipo='SALIDA').count()

    stock_actual = Inventario.objects.filter(cantidad__gt=0)
    total_prods_stock = stock_actual.count()
    
    valor_total_venta = stock_actual.aggregate(
        total=Sum(F('cantidad') * F('producto__precio_venta'), output_field=DecimalField())
    )['total'] or 0

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
        'movimientos_periodo': movimientos_periodo[:10],
        'total_movimientos': total_movs,
        'entradas': entradas,
        'salidas': salidas,
        'total_productos_stock': total_prods_stock,
        'total_valor_venta': valor_total_venta,
        'total_ganancia_proyectada': ganancia_proyectada,
    })



@login_required
def lista_categorias(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        
        Categorias.objects.create( # <-- Actualizado a Categoria
            nombre=nombre,
            descripcion=descripcion 
        )
        return redirect('inventario:lista_categorias')
    
    todas_las_categorias = Categorias.objects.all() # <-- Actualizado a Categoria
    return render(request, 'inventario/categorias.html', {
        'categorias': todas_las_categorias,
        'active_page': 'categorias'
    })


@login_required
def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categorias, id=id) # <-- Actualizado a Categoria
    categoria.delete()
    return redirect('inventario:lista_categorias')


@login_required
def lista_almacenes(request):
    return render(request, 'inventario/almacen.html', {'active_page': 'almacen'})



@staff_member_required # Solo permite el acceso si el usuario es "Staff"
def gestion_usuarios(request):
    if request.method == "POST":
        nombre_usuario = request.POST.get('username')
        clave = request.POST.get('password')
        es_admin = request.POST.get('es_admin') # Un checkbox en el HTML

        if User.objects.filter(username=nombre_usuario).exists():
            messages.error(request, "El nombre de usuario ya existe.")
        else:
            # Crear el usuario
            nuevo_usuario = User.objects.create_user(username=nombre_usuario, password=clave)
            
            # Si marcaron que es admin, le damos permisos de Staff
            if es_admin:
                nuevo_usuario.is_staff = True
                nuevo_usuario.save()
            
            messages.success(request, f"Usuario {nombre_usuario} creado con éxito.")
            return redirect('gestion_usuarios')

    usuarios = User.objects.all()
    return render(request, 'inventario/usuarios.html', {
        'usuarios': usuarios,
        'active_page': 'usuarios'
    })