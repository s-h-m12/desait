from django.db import models
from django.contrib.auth.models import AbstractUser

class Postavshik(models.Model):
    name = models.CharField()

class Articul(models.Model):
    name = models.CharField()

class Role(models.Model):
    name = models.CharField()

class Street(models.Model):
    name = models.CharField()

class Proizvoditel(models.Model):
    name = models.CharField()

class Status(models.Model):
    name = models.CharField()

class CustomUser(AbstractUser):
    middle_name = models.CharField()
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='customuser',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='customuser',
    )

class DeliveryService(models.Model):
    city = models.CharField()
    street = models.ForeignKey(Street, on_delete=models.CASCADE)
    house = models.IntegerField()
    index = models.IntegerField()

class Order(models.Model):
    order_date = models.DateField()
    delivery_date = models.DateField()
    delivery_service = models.ForeignKey(DeliveryService, on_delete=models.CASCADE)
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    delivery_code = models.IntegerField()
    status = models.ForeignKey(Status, on_delete=models.CASCADE)

class ArticulOrder(models.Model):
    articul = models.ForeignKey(Articul, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()

class Product(models.Model):
    articul = models.ForeignKey(Articul, on_delete=models.CASCADE)
    name = models.CharField()
    unit = models.CharField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    postavshik = models.ForeignKey(Postavshik, on_delete=models.CASCADE)
    proizvoditel = models.ForeignKey(Proizvoditel, on_delete=models.CASCADE)
    category = models.CharField()
    sale = models.IntegerField()
    quantity_on_warehouse = models.IntegerField()
    description = models.TextField()
    photo = models.CharField()