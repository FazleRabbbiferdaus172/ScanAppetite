from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from core.admin import custom_admin_site


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    # Add the 'user_type' field to the display and fieldsets
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'user_type', 'is_vendor_approved')
    list_filter = ('user_type',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type',)}),
    )
    actions = ['approve_vendors']

    def approve_vendors(self, request, queryset):
        for user in queryset:
            if user.user_type == 'VENDOR':
                user.profile.is_approved = True
                user.profile.save()
        self.message_user(request, "Selected vendors have been approved.")
    approve_vendors.short_description = "Approve selected vendors"

    def is_vendor_approved(self, obj):
        if obj.user_type == 'VENDOR':
            return obj.profile.is_approved
        return None
    is_vendor_approved.boolean = True # Shows a nice icon
    is_vendor_approved.short_description = 'Vendor Approved'


custom_admin_site.register(CustomUser, CustomUserAdmin)