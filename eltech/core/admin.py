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


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Product)
admin.site.register(models.Category)
admin.site.register(models.WeeklyDeal)
admin.site.register(models.Post)
admin.site.register(models.Order)
admin.site.register(models.Cart)
