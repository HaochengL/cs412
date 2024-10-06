# admin.py
# Author: Haocheng Liu (easonlhc@bu.edu)
# Description: This file registers the Profile model with the Django admin interface 
# so that the model can be managed via the admin interface.

from django.contrib import admin

# Register your models here.
from .models import Profile

admin.site.register(Profile)
