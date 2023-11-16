""" Django Admin Customization """

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as tr

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""

    ordering = ['id']
    list_display = ['email', 'name']
    readonly_fields = ['last_login']
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'email_confirmed',
                    'password',
                    'mobile_phone',
                    'profile_picture',
                    'birth_date',
                    'country',
                    'is_subscribed',
                    'facebook_profile',
                    'instagram_profile',
                    'twitter_profile'
                )
            }
        ),
        (
            tr('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }
        ),
        (
            tr('Important dates'),
            {
                'fields': (
                    'last_login',
                )
            }
        )
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'name',
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }
        ),
    )


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 1


class ProductFeatureInline(admin.TabularInline):
    model = models.ProductFeature
    extra = 1


class RatingInline(admin.TabularInline):
    model = models.Rating
    extra = 1


class ReviewInline(admin.TabularInline):
    model = models.Review
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductFeatureInline,
               RatingInline, ReviewInline]
    list_display = ('name', 'price', 'is_hot', 'is_on_sale', 'is_weekly_deal')
    list_filter = ('is_hot', 'is_on_sale')

    def is_weekly_deal(self, obj):
        """Return whether the product is a weekly deal."""
        return obj.weeklydeal_set.exists()

    is_weekly_deal.boolean = True


class ProductInline(admin.TabularInline):
    model = models.Product
    extra = 1


class PostInline(admin.TabularInline):
    model = models.Post
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductInline, PostInline]
    list_display = ['name']


class CommentInline(admin.TabularInline):
    model = models.Comment
    extra = 1


class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
    # Customize the displayed fields if needed
    list_display = ('title', 'user', 'created_at', 'updated_at')
    search_fields = ('title', 'content')  # Add fields you want to search
    list_filter = ('user', 'created_at')


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'logo')
    search_fields = ('title', 'description')


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.WeeklyDeal)
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Order)
admin.site.register(models.Cart)
admin.site.register(models.Service)
admin.site.register(models.CartProduct)
admin.site.register(models.Coupon)
