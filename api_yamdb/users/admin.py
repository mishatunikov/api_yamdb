from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


UserAdmin.fieldsets += (
    ('Extra fields', {'fields': ('role', 'bio', )}),
)

admin.site.register(CustomUser, UserAdmin)
