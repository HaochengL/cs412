# mini_fb/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, StatusMessage, Image
from django.forms import inlineformset_factory

class UserRegistrationForm(UserCreationForm):
    """
    Form for registering a new user account.
    Extends Django's built-in UserCreationForm to include email.
    """
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CreateProfileForm(forms.ModelForm):
    """
    Form for creating a new Profile.
    Excludes the user field as it will be set programmatically.
    """
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email_address', 'profile_image']

class CreateStatusMessageForm(forms.ModelForm):
    """
    Form for creating a new StatusMessage.
    """
    class Meta:
        model = StatusMessage
        fields = ['message']

class UpdateProfileForm(forms.ModelForm):
    """
    Form for updating an existing Profile.
    Excludes the user field to prevent changes to the associated User.
    """
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email_address', 'profile_image']

class UpdateStatusMessageForm(forms.ModelForm):
    """
    Form for updating an existing StatusMessage.
    """
    class Meta:
        model = StatusMessage
        fields = ['message']

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image_file']

# 定义一个 inline formset 工厂，用于 StatusMessage 和 Image
ImageFormSet = inlineformset_factory(
    StatusMessage,
    Image,
    form=ImageForm,
    fields=['image_file'],
    extra=1,
    can_delete=True
)
