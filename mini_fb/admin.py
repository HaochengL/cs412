# admin.py
# Author: Haocheng Liu (easonlhc@bu.edu)
# Description: This file registers the Profile model with the Django admin interface 
# so that the model can be managed via the admin interface.

from django.contrib import admin

# Register your models here.
from .models import Profile, StatusMessage, Image, Friend

class FriendAdmin(admin.ModelAdmin):
    list_display = ('profile1', 'profile2', 'timestamp')

admin.site.register(Profile)
admin.site.register(Friend, FriendAdmin)
# Register the StatusMessage model
admin.site.register(StatusMessage)

# Register the Image model
admin.site.register(Image)