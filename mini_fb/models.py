# models.py
# Author: Haocheng Liu (easonlhc@bu.edu)
# Username: easonlhc@bu.edu
# Description: This file defines the Profile and StatusMessage models for the mini Facebook application.
#              Profile model stores user profile information such as first name, last name, city, email, 
#              and profile image URL, while StatusMessage model stores messages associated with profiles.

from django.db import models
from django.urls import reverse

class Profile(models.Model):
    """
    Represents a user profile in the mini Facebook application.

    Attributes:
    first_name (str): The user's first name.
    last_name (str): The user's last name.
    city (str): The city where the user resides.
    email_address (str): The user's email address.
    profile_image_url (str): A URL pointing to the user's profile image (optional).
    """
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    city = models.CharField(max_length=50)
    email_address = models.EmailField()
    profile_image_url = models.URLField(blank=True)

    def __str__(self):
        """
        Returns a string representation of the Profile, showing the first and last name.
        """
        return f"{self.first_name} {self.last_name}"
    
    def get_status_messages(self):
        """
        Retrieves all status messages associated with this profile, ordered by timestamp in descending order.

        Returns:
        QuerySet: A queryset of StatusMessage objects associated with this profile.
        """
        return StatusMessage.objects.filter(profile=self).order_by('-timestamp')
    
    def get_absolute_url(self):
        """
        Returns the absolute URL to access the detail page for this profile.

        Returns:
        str: The URL that points to the profile's detail page.
        """
        return reverse('show_profile', kwargs={'pk': self.pk})
    
class StatusMessage(models.Model):
    """
    Represents a status message posted by a user profile.

    Attributes:
    timestamp (DateTime): The time the message was created.
    message (str): The content of the status message.
    profile (ForeignKey): The profile associated with this status message.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        """
        Returns a string representation of the StatusMessage, showing the message ID and content.
        """
        return f"StatusMessage(id={self.id}, message='{self.message}')"
    
    def get_images(self):
        '''Return all images associated with this StatusMessage.'''
        return Image.objects.filter(status_message=self)
    

from django.db import models
from .models import StatusMessage  # Import StatusMessage to create FK

class Image(models.Model):
    '''Encapsulate the idea of an image uploaded to a StatusMessage.'''
    image_file = models.ImageField(blank=True, upload_to='images/')  # Add this field
    timestamp = models.DateTimeField(auto_now_add=True)
    status_message = models.ForeignKey(StatusMessage, on_delete=models.CASCADE)
