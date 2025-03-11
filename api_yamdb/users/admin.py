from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_editable = ('role', 'is_staff', 'is_active')
    list_filter = UserAdmin.list_filter + ('role',)


CustomAdmin.fieldsets += (('Extra fields', {'fields': ('role', 'bio')}),)
admin.site.register(CustomUser, CustomAdmin)
