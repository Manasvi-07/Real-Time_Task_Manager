from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .views import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email','role','is_staff','is_active')
    list_filter = ('role','is_staff', 'is_active')
    fieldsets = (
        (None, {'fields' : ('email','password')}),
        ('permissions', {'fields':('is_staff', 'is_active', 'is_superuser','groups','user_permissions')}),
        ('Role Info', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes':('wide',),
            'fields':('email','password1','password2','role','is_staff','is_active')
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
