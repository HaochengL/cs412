# mini_fb/admin.py

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, Friend, StatusMessage, Image

# Define Profile inline
class ProfileInline(admin.TabularInline):
    model = Profile
    extra = 1
    can_delete = True
    verbose_name_plural = 'Profiles'

# Define StatusMessage inline
class StatusMessageInline(admin.TabularInline):
    model = StatusMessage
    extra = 1
    verbose_name_plural = 'Status Messages'

# Define Image inline
class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    verbose_name_plural = 'Images'

# Custom UserAdmin with ProfileInline
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_profile_first_name', 'is_staff')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('profiles')

    def first_profile_first_name(self, instance):
        """Display first profile's first name"""
        first_profile = instance.profiles.first()
        return first_profile.first_name if first_profile else '-'
    first_profile_first_name.short_description = 'First Profile First Name'

# Unregister original UserAdmin
admin.site.unregister(User)

# Register new UserAdmin
admin.site.register(User, CustomUserAdmin)

# Register Profile admin with StatusMessage inline
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'email_address')
    search_fields = ('user__username', 'first_name', 'last_name', 'email_address')
    list_filter = ('city',)
    inlines = [StatusMessageInline]  # Only StatusMessage inline

# Register Friend admin
@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('profile1', 'profile2', 'timestamp')
    search_fields = (
        'profile1__first_name', 'profile1__last_name',
        'profile2__first_name', 'profile2__last_name'
    )
    list_filter = ('timestamp',)

# Register StatusMessage admin with Image inline
@admin.register(StatusMessage)
class StatusMessageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'message', 'timestamp')
    search_fields = ('message', 'profile__first_name', 'profile__last_name')
    list_filter = ('timestamp',)
    inlines = [ImageInline]  # Image inline in StatusMessage

# Register Image admin
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('status_message', 'image_file', 'timestamp')
    search_fields = ('status_message__message',)
    list_filter = ('timestamp',)
