from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import CustomUser, Product, Role, Articul


def guest_login_view(request):
    # Получаем или создаем роль "Гость"
    try:
        guest_role, created = Role.objects.get_or_create(
            name='Гость',
            defaults={'name': 'Гость'}
        )

        # Получаем или создаем гостевого пользователя
        guest_user, created = CustomUser.objects.get_or_create(
            username='guest_user',
            defaults={
                'first_name': 'Гость',
                'last_name': 'Пользователь',
                'middle_name': 'Анонимный',
                'email': 'guest@example.com',
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
                'role': guest_role
            }
        )

        # Если пользователь был создан, устанавливаем пароль
        if created:
            guest_user.set_password('guest_password_123')
            guest_user.save()

        # Выполняем вход гостя
        login(request, guest_user)
        return redirect('home')

    except Exception as e:
        # В случае ошибки делаем пользователя анонимным
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        return redirect('home')


@login_required
def index_view(request):
    products = Product.objects.all()
    # Получаем параметры фильтрации из GET запроса
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '')
    filterer = request.GET.get('filterer', '')
    # Получаем уникальные категории для фильтра
    categories = products.values_list('category', flat=True).distinct().order_by('category')
    # Фильтрация по поисковому запросу
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(category__icontains=search) | Q(description__icontains=search))
    # Сортировка по количеству на складе
    if sort == 'name_asc':
        products = products.order_by('quantity_on_warehouse')
    elif sort == 'name_desc':
        products = products.order_by('-quantity_on_warehouse')
    # Фильтрация по категории
    if filterer:
        products = products.filter(category=filterer)
    return render(request, 'index.html', {'products': products, 'search': search, 'sort': sort,
                                          'filterer': filterer, 'categories': categories})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Неверные данные'})
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def delete_view(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('home')


def create_view(request):
    if request.method == 'POST':
        # Создаем артикул и товар
        articul_name = request.POST.get('art_name')
        articul = Articul.objects.create(name=articul_name)
        product = (Product.objects.create
            (
            articul_id=articul.id,
            name=request.POST.get('name'),
            unit=request.POST.get('unit'),
            price=request.POST.get('price'),
            postavshik_id=request.POST.get('postavshik'),
            proizvoditel_id=request.POST.get('proizvoditel'),
            category=request.POST.get('category'),
            sale=request.POST.get('sale'),
            quantity_on_warehouse=request.POST.get('quantity'),
            description=request.POST.get('description'),
            photo=request.POST.get('photo')
        ))
        return redirect('home')
    return render(request, 'prod.html')


def update_view(request, id):
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        product.name = request.POST.get('name'),
        product.unit = request.POST.get('unit'),
        product.price = request.POST.get('price'),
        product.postavshik = request.POST.get('postavshik'),
        product.proizvoditel = request.POST.get('proizvoditel'),
        product.category = request.POST.get('category'),
        product.sale = request.POST.get('sale'),
        product.quantity_on_warehouse = request.POST.get('quantity'),
        product.description = request.POST.get('description'),
        product.photo = request.POST.get('photo')
        product.save()
        return redirect('home')
    return render(request, 'prod.html', {'product': product})