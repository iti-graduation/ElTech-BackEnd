""" Database models """

import uuid
import os
from datetime import datetime

from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission
)


def product_image_file_path(instance, filename):
    """Generate file path for new product image"""

    # get the extension of the file (png/jpg/etc..)
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'product', filename)


def category_image_file_path(instance, filename):
    """Generate file path for new category image"""

    # get the extension of the file (png/jpg/etc..)
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'category', filename)


def post_image_file_path(instance, filename):
    """Generate file path for new post image"""

    # get the extension of the file (png/jpg/etc..)
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'post', filename)


def profile_image_file_path(instance, filename):
    """Generate file path for new profile image"""

    # get the extension of the file (png/jpg/etc..)
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'profile', filename)


def service_image_file_path(instance, filename):
    """Generate file path for new profile image"""

    # get the extension of the file (png/jpg/etc..)
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'service', filename)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""

    email = models.EmailField(max_length=255, unique=True)
    email_confirmed = models.BooleanField(default=False)
    mobile_phone = models.CharField(max_length=15, unique=True)
    profile_picture = models.ImageField(
        upload_to=profile_image_file_path,
        null=True,
        blank=True
    )
    birth_date = models.DateField(null=True, blank=True)
    # name = models.CharField(max_length=255)
    country = models.CharField(max_length=50, null=True, blank=True)
    facebook_profile = models.URLField(null=True, blank=True)
    instagram_profile = models.URLField(null=True, blank=True)
    twitter_profile = models.URLField(null=True, blank=True)
    is_subscribed = models.BooleanField(default=False)
    activation_sent_date = models.DateTimeField(default=datetime.now)

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    @property
    def name(self):
        """Returns the full name of the user."""

        return f'{self.first_name} {self.last_name}'


class Category(models.Model):
    """Category object"""
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=category_image_file_path)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product object"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    stock = models.PositiveIntegerField()
    view_count = models.PositiveIntegerField(default=0)
    is_hot = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    sale_amount = models.PositiveSmallIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name


class Rating(models.Model):
    """Rating object"""
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        default=1
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='ratings')


class Review(models.Model):
    """Review object"""
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')


class ProductImage(models.Model):
    """Product image object"""
    image = models.ImageField(upload_to=product_image_file_path)
    is_thumbnail = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return self.image.url


class ProductFeature(models.Model):
    """Product feature object"""
    feature = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='features')

    def __str__(self):
        return self.feature


class WeeklyDeal(models.Model):
    deal_time = models.DateField(null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Favorite(models.Model):
    """Favorite product object"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Coupon(models.Model):
    """Coupon object"""
    code = models.CharField(max_length=255)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    uses_limit = models.PositiveSmallIntegerField(default=0)


class Cart(models.Model):
    """Cart object"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartProduct')
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def total_price(self):
        total = sum(cp.total_price for cp in self.cartproduct_set.all())
        if self.coupon:
            total *= (1 - self.coupon.discount/100)
        return total


class CartProduct(models.Model):
    """Cart product object"""
    quantity = models.PositiveIntegerField(default=1)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """Order object"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=5, decimal_places=2)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderProduct')

    @property
    def total_price(self):
        total = sum(cp.total_price for cp in self.orderproduct_set.all())
        # if self.coupon:
        #     total *= (1 - self.coupon.discount)
        return total


class OrderProduct(models.Model):
    """Order product object"""
    quantity = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Post(models.Model):
    """Post object"""
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to=post_image_file_path)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comment object"""
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"by: {self.user.email}, id: {self.id}"


class Service(models.Model):
    """Service object"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to=service_image_file_path)

    def __str__(self):
        return self.title
