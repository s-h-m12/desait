from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import CustomUser, Product, Role


def guest_login_view(request):
    try:
        guest_role, created = Role.objects.get_or_create(
            name='Гость',
            defaults={'name': 'Гость'}
        )

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

        if created:
            guest_user.set_password('guest_password_123')
            guest_user.save()

        login(request, guest_user)
        return redirect('home')

    except Exception as e:
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        return redirect('home')


@login_required
def index_view(request):
    products = Product.objects.all()
    search = request.GET.get('search', '')
    sort = request.GET.get('sort','')
    if search:
        products = products.filter(name__icontains=search)
    if sort == 'name_asc':
        products = products.order_by('name')
    return render(request, 'index.html', {'products': products, 'search': search, 'sort': sort})

def login_view(request):
    if request.method == 'POST':
         username = request.POST.get('username', '')
         password = request.POST.get('password', '')
         user = authenticate(request,username=username,password=password)
         if user is not None:
             login(request,user)
             return redirect('home')
         else:
             return render(request,'login.html',{'error':'Неверные данные'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
