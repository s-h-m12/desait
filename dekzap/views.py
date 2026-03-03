from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import CustomUser, Product, Role, Articul, Postavshik, Proizvoditel, Order, ArticulOrder, Status


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
    postavshiki = Postavshik.objects.all()
    # Получаем параметры фильтрации из GET запроса
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '')
    filterer = request.GET.get('filterer', '')
    filterer_postav = request.GET.get('filterer_postav', '')
    # Получаем уникальные категории для фильтра
    categories = products.values_list('category', flat=True).distinct().order_by('category')
    # Фильтрация по поисковому запросу
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search))
    # Фильтрация по категории
    if filterer:
        products = products.filter(category=filterer)
    if filterer_postav:
        products = products.filter(postavshik_id=filterer_postav)
    # Сортировка по количеству на складе
    if sort == 'name_asc':
        products = products.order_by('quantity_on_warehouse')
    elif sort == 'name_desc':
        products = products.order_by('-quantity_on_warehouse')
    return render(request, 'index.html', {'products': products, 'search': search, 'sort': sort,
                                          'filterer': filterer, 'categories': categories,
                                          'postavshiki': postavshiki})


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
    proizvoditels = Proizvoditel.objects.all()
    categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
    postavshiki = Postavshik.objects.all()

    if request.method == 'POST':
        # Получаем данные
        articul_name = request.POST.get('art_name')
        postavshik_id = request.POST.get('postavshik')

        # Создаем или получаем артикул
        articul, _ = Articul.objects.get_or_create(name=articul_name)

        # Создаем товар
        Product.objects.create(
            articul=articul,
            name=request.POST.get('name'),
            unit=request.POST.get('unit'),
            price=request.POST.get('price'),
            postavshik_id=postavshik_id,
            proizvoditel_id=request.POST.get('proizvoditel'),
            category=request.POST.get('category'),
            sale=request.POST.get('sale'),
            quantity_on_warehouse=request.POST.get('quantity'),
            description=request.POST.get('description'),
            photo=request.FILES.get('photo')
        )
        return redirect('home')

    return render(request, 'prod.html', {
        'proizvoditels': proizvoditels,
        'categories': categories,
        'postavshiki': postavshiki,
        'is_update': False
    })
def update_view(request, id):
    product = Product.objects.get(id=id)
    proizvoditels = Proizvoditel.objects.all()
    categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
    postavshiki = Postavshik.objects.all()

    if request.method == 'POST':
        # Обновляем поля
        product.name = request.POST.get('name')
        product.unit = request.POST.get('unit')
        product.price = request.POST.get('price')
        product.postavshik_id = request.POST.get('postavshik')  # изменил на postavshik
        product.proizvoditel_id = request.POST.get('proizvoditel')
        product.category = request.POST.get('category')
        product.sale = request.POST.get('sale')
        product.quantity_on_warehouse = request.POST.get('quantity')
        product.description = request.POST.get('description')

        articul_name = request.POST.get('art_name')
        if articul_name and product.articul.name != articul_name:
            articul, created = Articul.objects.get_or_create(name=articul_name)
            product.articul = articul

        if request.FILES.get('photo'):
            product.photo = request.FILES.get('photo')

        product.save()
        return redirect('home')

    return render(request, 'prod.html', {
        'product': product,
        'proizvoditels': proizvoditels,
        'categories': categories,
        'postavshiki': postavshiki,
        'is_update': True
    })

@login_required
def orders_view(request):
    orders = Order.objects.select_related('client', 'delivery_service', 'status'
                                          ).prefetch_related('articulorder_set__articul__product_set'
                                                             ).all()
    return render(request, 'orders.html', {'orders': orders})

def delete_order_view(request, id):
    product = Order.objects.get(id=id)
    product.delete()
    return redirect('orders')


def create_order_view(request):
    statuses = Status.objects.all()
    orders = Order.objects.select_related('client', 'delivery_service', 'status'
                                          ).prefetch_related('articulorder_set__articul'
                                                             ).all()

    if request.method == 'POST':
        # Получаем данные
        articul_name = request.POST.get('art_name')

        # Создаем или получаем артикул
        articul = Articul.objects.get_or_create(name=articul_name)[0]

        order = Order()
        order.order_date = request.POST.get('order_date')
        order.delivery_date = request.POST.get('delivery_date')
        order.delivery_code = request.POST.get('delivery_code')
        order.client_id = request.POST.get("client")
        order.delivery_service_id = request.POST.get("delivery_service")
        order.status_id = request.POST.get("status")
        order.save()

        articulorder = ArticulOrder()
        articulorder.quantity = request.POST.get('quantity')
        articulorder.articul_id = articul.id
        articulorder.order_id = order.id
        articulorder.save()
        return redirect('orders')

    return render(request, 'prod.html', {
        'statuses': statuses,
        'orders': orders,
        'is_update': False
    })
def update_order_view(request, id):
   # order = Order.objects.get(id=id)
    proizvoditels = Proizvoditel.objects.all()
    categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
    postavshiki = Postavshik.objects.all()

 #   if request.method == 'POST':
  #      # Обновляем поля
   #     product.name = request.POST.get('name')
    #    product.unit = request.POST.get('unit')
     #   product.price = request.POST.get('price')
      #  product.postavshik_id = request.POST.get('postavshik')  # изменил на postavshik
       # product.proizvoditel_id = request.POST.get('proizvoditel')
        #product.category = request.POST.get('category')
        #product.sale = request.POST.get('sale')
        #product.quantity_on_warehouse = request.POST.get('quantity')
        #product.description = request.POST.get('description')

    #    articul_name = request.POST.get('art_name')
        #if articul_name and product.articul.name != articul_name:
          #  articul, created = Articul.objects.get_or_create(name=articul_name)
         #   product.articul = articul

   #     order.save()
    #    return redirect('home')

 #   return render(request, 'prod.html', {
  #      'order': order,
  #      'proizvoditels': proizvoditels,
   #     'categories': categories,
   #     'postavshiki': postavshiki,
 #       'is_update': True
  #  })

