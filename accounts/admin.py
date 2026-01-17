from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, EducatorProfile

class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'user_type', 'is_staff']
    list_filter = ['user_type', 'is_staff', 'is_active']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type',)}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'user_type',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentProfile)
admin.site.register(EducatorProfile)