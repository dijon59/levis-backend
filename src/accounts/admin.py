from django.contrib import admin
from src.accounts.models import User, FCMDeviceToken
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_customer', 'is_employee']
    ordering = ('email',)
    search_fields = ['email']

    list_filter = ['is_active', 'is_employee']

    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        ('Personal info', {'fields': ('name', 'first_name', 'last_name', 'contact_number')}),
        ('Permissions', {'fields': ('is_active', 'is_employee', 'is_customer', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',
                       'first_name',
                       'last_name',
                       'contact_number',
                       'password1',
                       'password2'),
        }),
    )


@admin.register(FCMDeviceToken)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_token', 'updated_at']
