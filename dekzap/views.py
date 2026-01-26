from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import CustomUser, Product

@login_required
def index_view(request):
    products = Product.objects.all()
    search = request.GET.get('search', '')
    sort = request.GET.get('sort','')
    if search:
        products = products.filter(name=search)
    if sort:
        products = products.order_by('name')
    return render(request, 'index.html', {'products': products, 'search': search})

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
