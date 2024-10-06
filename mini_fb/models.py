# models.py
# Author: Haocheng Liu (easonlhc@bu.edu)
# Description: This file defines the Profile model for the mini_fb application, 
# which stores user profile information such as first name, last name, city, email, and profile image URL.

from django.db import models

# Create your models here.
from django.db import models

class Profile(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    city = models.CharField(max_length=50)
    email_address = models.EmailField()
    profile_image_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
