from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeNumericFilter, RangeDateFilter
from .models import CustomUser, Contact


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', ('created_at', RangeDateFilter))
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')
    
    ordering = ('-created_at',)


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone'),
        }),
        ('Message Details', {
            'fields': ('subject', 'message'),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    list_display = ('first_name', 'last_name', 'email', 'subject', 'phone', 'created_at')
    list_filter = ('subject', ('created_at', RangeDateFilter))
    search_fields = ('first_name', 'last_name', 'email', 'message')
    readonly_fields = ('created_at',)
    
    ordering = ('-created_at',)
    
    # def has_delete_permission(self, request):
    #     return request.user.is_superuser
    

