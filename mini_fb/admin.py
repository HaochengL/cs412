# mini_fb/admin.py

# Author: Haocheng Liu (easonlhc@bu.edu)
# Description: Registers the Profile, Friend, StatusMessage, and Image models with the Django admin interface.
#              Enhances admin functionalities with custom display options.

from django.contrib import admin
from .models import Profile, Friend, StatusMessage, Image

class FriendAdmin(admin.ModelAdmin):
    list_display = ('profile1', 'profile2', 'timestamp')
    search_fields = ('profile1__first_name', 'profile1__last_name', 'profile2__first_name', 'profile2__last_name')

class StatusMessageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'message', 'timestamp')
    search_fields = ('message', 'profile__first_name', 'profile__last_name')
    list_filter = ('timestamp',)

class ImageAdmin(admin.ModelAdmin):
    list_display = ('status_message', 'image_file', 'timestamp')
    search_fields = ('status_message__message',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'email_address')
    search_fields = ('user__username', 'first_name', 'last_name', 'email_address')
    list_filter = ('city',)
    # Display inline StatusMessages and Images
    inlines = []

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Friend, FriendAdmin)
admin.site.register(StatusMessage, StatusMessageAdmin)
admin.site.register(Image, ImageAdmin)
