# mini_fb/models.py

from django.db import models
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User

class Profile(models.Model):
    """
    Represents a user profile in the Mini Facebook application.
    
    Attributes:
        user (ForeignKey): The associated Django User for authentication.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        city (str): The city where the user resides.
        email_address (str): The user's email address.
        profile_image (ImageField): The user's profile image.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    city = models.CharField(max_length=50)
    email_address = models.EmailField()
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def get_news_feed(self):
        """Retrieve all StatusMessages for this Profile and its friends, ordered by timestamp descending."""
        friends = self.get_friends()
        friends_ids = [friend.id for friend in friends]
        friends_ids.append(self.id)  # Include own StatusMessages

        news_feed = StatusMessage.objects.filter(profile__id__in=friends_ids).select_related('profile').order_by('-timestamp')
        return news_feed

    def __str__(self):
        """String representation of the Profile."""
        return f"{self.first_name} {self.last_name}"

    def get_status_messages(self):
        """Retrieve all StatusMessages associated with this Profile, ordered by timestamp descending."""
        return StatusMessage.objects.filter(profile=self).order_by('-timestamp')

    def get_absolute_url(self):
        """Return the absolute URL to access the detail page for this Profile."""
        return reverse('show_profile', kwargs={'pk': self.pk})

    def get_friends(self):
        """Return a list of Profiles that are friends with this Profile."""
        friends_relations1 = Friend.objects.filter(profile1=self)
        friends_relations2 = Friend.objects.filter(profile2=self)
        friends = [relation.profile2 for relation in friends_relations1] + [relation.profile1 for relation in friends_relations2]
        return friends

    def add_friend(self, other):
        """Add a friendship relation between this Profile and another Profile."""
        if self == other:
            return  # Prevent self-friending

        # Ensure consistent ordering to prevent duplicate friendships
        if self.id < other.id:
            profile1, profile2 = self, other
        else:
            profile1, profile2 = other, self

        # Check if the friendship already exists
        existing_friend = Friend.objects.filter(
            profile1=profile1,
            profile2=profile2
        ).first()

        if not existing_friend:
            Friend.objects.create(profile1=profile1, profile2=profile2)

    def get_friend_suggestions(self):
        """Return a list of Profile objects that are suggested friends."""
        # Get current friends
        friends = self.get_friends()
        friends_ids = [friend.id for friend in friends]
        friends_ids.append(self.id)  # Exclude self

        # Get friends of friends excluding current friends and self
        friends_of_friends = Friend.objects.filter(
            Q(profile1__in=friends) | Q(profile2__in=friends)
        ).exclude(
            Q(profile1=self) | Q(profile2=self)
        )

        suggestions_ids = set()
        for relation in friends_of_friends:
            if relation.profile1 != self and relation.profile1.id not in friends_ids:
                suggestions_ids.add(relation.profile1.id)
            if relation.profile2 != self and relation.profile2.id not in friends_ids:
                suggestions_ids.add(relation.profile2.id)

        suggestions = Profile.objects.filter(id__in=suggestions_ids).distinct()
        return suggestions

class Friend(models.Model):
    """
    Represents a friendship relation between two Profiles.
    
    Attributes:
        profile1 (ForeignKey): One Profile in the friendship.
        profile2 (ForeignKey): The other Profile in the friendship.
        timestamp (DateTime): When the friendship was established.
    """
    profile1 = models.ForeignKey(Profile, related_name="profile1_friends", on_delete=models.CASCADE)
    profile2 = models.ForeignKey(Profile, related_name="profile2_friends", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String representation of the friendship."""
        return f"{self.profile1} & {self.profile2}"

    class Meta:
        unique_together = ('profile1', 'profile2')  # Prevent duplicate friendships

class StatusMessage(models.Model):
    """
    Represents a status message posted by a Profile.
    
    Attributes:
        timestamp (DateTime): When the status message was created.
        message (str): The content of the status message.
        profile (ForeignKey): The Profile that posted the status message.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        """String representation of the StatusMessage."""
        return f"StatusMessage(id={self.id}, message='{self.message[:20]}...')"

    def get_images(self):
        """Return all Images associated with this StatusMessage."""
        return Image.objects.filter(status_message=self)

class Image(models.Model):
    """
    Represents an image uploaded to a StatusMessage.
    
    Attributes:
        image_file (ImageField): The uploaded image file.
        timestamp (DateTime): When the image was uploaded.
        status_message (ForeignKey): The StatusMessage associated with this image.
    """
    image_file = models.ImageField(upload_to='images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status_message = models.ForeignKey(StatusMessage, on_delete=models.CASCADE)

    def __str__(self):
        """String representation of the Image."""
        return f"Image(id={self.id}, status_message_id={self.status_message.id})"
