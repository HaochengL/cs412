# mini_fb/admin.py

# Author: Haocheng Liu (easonlhc@bu.edu)
# Description: Registers the Profile, Friend, StatusMessage, and Image models with the Django admin interface.
#              Enhances admin functionalities with custom display options and inlines.

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, Friend, StatusMessage, Image

# 定义 Profile 的内联类
class ProfileInline(admin.TabularInline):
    model = Profile
    extra = 1  # 默认显示一个额外的空表单
    can_delete = True  # 允许删除
    verbose_name_plural = 'Profiles'  # 内联部分的标题

# 定义 StatusMessage 的内联类
class StatusMessageInline(admin.TabularInline):
    model = StatusMessage
    extra = 1  # 默认显示一个额外的空表单
    verbose_name_plural = 'Status Messages'

# 定义 Image 的内联类
class ImageInline(admin.TabularInline):
    model = Image
    extra = 1  # 默认显示一个额外的空表单
    verbose_name_plural = 'Images'

# 定义一个自定义的 UserAdmin，包含 ProfileInline
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)  # 添加内联类
    list_display = ('username', 'email', 'first_profile_first_name', 'is_staff')  # 显示的字段

    # 移除 list_select_related，因为 'profiles' 是反向关系，不能用在 select_related
    # 并添加 prefetch_related
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('profiles')

    def first_profile_first_name(self, instance):
        """显示第一个关联 Profile 的 first_name"""
        first_profile = instance.profiles.first()
        return first_profile.first_name if first_profile else '-'
    first_profile_first_name.short_description = 'First Profile First Name'

# 取消注册原始的 UserAdmin
admin.site.unregister(User)

# 注册新的 UserAdmin
admin.site.register(User, CustomUserAdmin)

# 注册 Profile 模型，并内联 StatusMessage（移除 ImageInline）
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'email_address')
    search_fields = ('user__username', 'first_name', 'last_name', 'email_address')
    list_filter = ('city',)
    inlines = [StatusMessageInline]  # 仅内联 StatusMessage

# 注册 Friend 模型
@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('profile1', 'profile2', 'timestamp')
    search_fields = (
        'profile1__first_name', 'profile1__last_name',
        'profile2__first_name', 'profile2__last_name'
    )
    list_filter = ('timestamp',)

# 注册 StatusMessage 模型，并内联 Image
@admin.register(StatusMessage)
class StatusMessageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'message', 'timestamp')
    search_fields = ('message', 'profile__first_name', 'profile__last_name')
    list_filter = ('timestamp',)
    inlines = [ImageInline]  # 允许在 StatusMessage 中内联显示 Images

# 注册 Image 模型
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('status_message', 'image_file', 'timestamp')
    search_fields = ('status_message__message',)
    list_filter = ('timestamp',)
