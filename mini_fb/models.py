# models.py
# Author: Haocheng Liu (easonlhc@bu.edu)
# Username: easonlhc@bu.edu
# Description: This file defines the Profile and StatusMessage models for the mini Facebook application.
#              Profile model stores user profile information such as first name, last name, city, email, 
#              and profile image URL, while StatusMessage model stores messages associated with profiles.

from django.db import models
from django.urls import reverse
from django.db.models import Q

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

    def get_news_feed(self):
        """获取当前Profile及其朋友的所有StatusMessages按时间降序排序"""
        friends = self.get_friends()
        friends_ids = [friend.id for friend in friends]
        friends_ids.append(self.id)  # 包含自己的StatusMessages

        news_feed = StatusMessage.objects.filter(profile__id__in=friends_ids).select_related('profile').order_by('-timestamp')
        return news_feed

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
    
    def get_friends(self):
        """返回该Profile的所有朋友列表"""
        friends_relations1 = Friend.objects.filter(profile1=self)
        friends_relations2 = Friend.objects.filter(profile2=self)
        friends = [relation.profile2 for relation in friends_relations1] + [relation.profile1 for relation in friends_relations2]
        return friends

    def add_friend(self, other):
        """添加朋友关系"""
        if self == other:
            return  # 不允许自我添加朋友
        # 检查是否已经是朋友
        existing_friend = Friend.objects.filter(
            (models.Q(profile1=self) & models.Q(profile2=other)) |
            (models.Q(profile1=other) & models.Q(profile2=self))
        ).first()
        if not existing_friend:
            Friend.objects.create(profile1=self, profile2=other)
    def get_friend_suggestions(self):
        """获取朋友建议，基于朋友的朋友"""
        # 获取当前的朋友列表
        friends = self.get_friends()
        friends_ids = [friend.id for friend in friends]
        friends_ids.append(self.id)  # 排除自己

        # 获取朋友的朋友（不包括自己和已有的朋友）
        friends_of_friends = Friend.objects.filter(
            Q(profile1__in=friends) | Q(profile2__in=friends)
        ).exclude(
            Q(profile1=self) | Q(profile2=self)
        )

        # 收集所有朋友的朋友的Profile IDs
        suggestions_ids = set()
        for friend_relation in friends_of_friends:
            if friend_relation.profile1 != self and friend_relation.profile1 not in friends:
                suggestions_ids.add(friend_relation.profile1.id)
            if friend_relation.profile2 != self and friend_relation.profile2 not in friends:
                suggestions_ids.add(friend_relation.profile2.id)

        # 返回建议的Profile列表
        suggestions = Profile.objects.filter(id__in=suggestions_ids).distinct()
        return suggestions

class Friend(models.Model):
    profile1 = models.ForeignKey(Profile, related_name="profile1_friends", on_delete=models.CASCADE)
    profile2 = models.ForeignKey(Profile, related_name="profile2_friends", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile1} & {self.profile2}"
    

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
