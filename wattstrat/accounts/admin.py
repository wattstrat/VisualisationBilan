from django.contrib import admin
from django.utils.translation import ugettext as _

from authtools import admin as authtools_admin

from wattstrat.accounts.models import Account, User


class AccountAdmin(admin.ModelAdmin):
    fields = ('corporate_name', 'department', 'address', 'phone', 'logo', 'communes')


class UserAdmin(authtools_admin.NamedUserAdmin):
    list_display = ('is_active', 'email', 'name', 'account', 'is_staff', 'date_joined')
    fieldsets = (
        (None, {
            'fields': ('email', 'name', 'account', 'password')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'email_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        authtools_admin.DATE_FIELDS
    )

admin.site.register(Account, AccountAdmin)
admin.site.register(User, UserAdmin)
