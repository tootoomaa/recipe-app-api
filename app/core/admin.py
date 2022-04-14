from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserManager
from django.utils.translation import gettext as _

from core import models

class UserAdmin(BaseUserManager):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),    # none=title, defin section
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2')
        }),
    )

admin.site.register(models.User, UserAdmin)
