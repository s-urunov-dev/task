from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (('user', 'User'), ('admin', 'Admin'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    objects = UserManager()


class Book(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='book_images')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title

    def clean(self):
        if self.price <= 0:
            raise ValidationError({'price': 'Narx 0 dan katta bo\'lishi kerak.'})


class Order(models.Model):
    user = models.ForeignKey('books.User', on_delete=models.CASCADE)
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

class Invoice(models.Model):
    order = models.OneToOneField('books.Order', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    invoice = models.ForeignKey('books.Invoice', on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    is_successful = models.BooleanField()
    paid_at = models.DateTimeField(auto_now_add=True)
