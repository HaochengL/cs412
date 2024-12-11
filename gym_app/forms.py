# gym_app/forms.py
# Author: Haocheng Liu <easonlhc@bu.edu>
# Description: This file contains Django form classes for user registration, profile management, workout sessions,
#              fitness metrics, suggestions, workout types, data filtering, and messaging.

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, WorkoutSession, FitnessMetric, Suggestion, WorkoutType, Message

class RegistrationForm(UserCreationForm):
    """
    Extends the built-in UserCreationForm to include an email field.
    Used for registering new users.
    """
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        # Specifies the fields to include in the registration form.
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        """
        Validates that the provided email is unique.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email


class WorkoutSessionForm(forms.ModelForm):
    """
    Form for creating and updating WorkoutSession instances.
    Includes a customized date input widget for session_date.
    """
    class Meta:
        model = WorkoutSession
        # Specifies the fields to include in the workout session form.
        fields = [
            'workout_type', 'session_date', 'session_duration_hours',
            'max_bpm', 'avg_bpm', 'resting_bpm'
        ]
        # Custom widget for the session_date field to use an HTML5 date picker.
        widgets = {
            'session_date': forms.DateInput(attrs={'type': 'date'}),
        }
        # Labels can be customized if needed; currently using default labels.


class ProfileForm(forms.ModelForm):
    """
    Form for creating and updating Profile instances.
    Includes an option to remove the current photo.
    """
    # Additional field to allow users to remove their current profile photo.
    remove_photo = forms.BooleanField(required=False, label='Remove current photo')

    class Meta:
        model = Profile
        # Specifies the fields to include in the profile form.
        fields = ['age', 'gender', 'weight_kg', 'height_m', 'experience_level', 'photo', 'remove_photo']
        # Custom labels or widgets can be added here if necessary.

    def save(self, commit=True):
        """
        Overrides the default save method to handle photo removal.
        If 'remove_photo' is checked, the existing photo is deleted.
        """
        profile = super().save(commit=False)
        if self.cleaned_data.get('remove_photo'):
            if profile.photo:
                # Deletes the photo file from storage without saving the model yet.
                profile.photo.delete(save=False)
            profile.photo = None  # Sets the photo field to None to remove it.
        if commit:
            profile.save()  # Saves the Profile instance to the database.
        return profile

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and customizes the photo field's clear checkbox label.
        """
        super(ProfileForm, self).__init__(*args, **kwargs)
        # Removes the default label for the clear checkbox to avoid displaying 'Clear' option.
        self.fields['photo'].widget.clear_checkbox_label = ''


class FitnessMetricForm(forms.ModelForm):
    """
    Form for creating and updating FitnessMetric instances.
    """
    class Meta:
        model = FitnessMetric
        # Specifies the fields to include in the fitness metric form.
        fields = ['fat_percentage', 'water_intake_liters']
        # Custom widgets or labels can be added here if necessary.


class SuggestionForm(forms.ModelForm):
    """
    Form for creating and updating Suggestion instances.
    """
    class Meta:
        model = Suggestion
        # Specifies the fields to include in the suggestion form.
        fields = ['suggestion_type', 'suggestion_text']
        # Custom widgets or labels can be added here if necessary.


class WorkoutTypeForm(forms.ModelForm):
    """
    Form for creating and updating WorkoutType instances.
    """
    class Meta:
        model = WorkoutType
        # Specifies the fields to include in the workout type form.
        fields = ['name', 'description']
        # Custom widgets or labels can be added here if necessary.


class DataFilterForm(forms.Form):
    """
    Form for filtering member data based on various criteria.
    Used in data visualization and analytics views.
    """
    GENDER_CHOICES = [
        ('All', 'All'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('All', 'All'),
        ('1', 'Beginner'),
        ('2', 'Intermediate'),
        ('3', 'Advanced'),
    ]

    WORKOUT_FREQUENCY_CHOICES = [
        ('All', 'All'),
        ('Low', '2 times/week or less'),
        ('High', '3 times/week or more'),
    ]

    # Choice field for gender with an option to select all genders.
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        label='Gender',
        initial='All'
    )

    # Integer field for specifying the minimum age filter.
    min_age = forms.IntegerField(
        required=False,
        label='Minimum Age',
        min_value=0,
        help_text="Enter the minimum age to filter by."
    )

    # Integer field for specifying the maximum age filter.
    max_age = forms.IntegerField(
        required=False,
        label='Maximum Age',
        min_value=0,
        help_text="Enter the maximum age to filter by."
    )

    # Choice field for experience level with an option to select all levels.
    experience_level = forms.ChoiceField(
        choices=EXPERIENCE_LEVEL_CHOICES,
        required=False,
        label='Experience Level',
        initial='All'
    )

    # Choice field for workout frequency with an option to select all frequencies.
    workout_frequency = forms.ChoiceField(
        choices=WORKOUT_FREQUENCY_CHOICES,
        required=False,
        label='Workout Frequency',
        initial='All'
    )


class MessageForm(forms.ModelForm):
    """
    Form for creating and updating Message instances.
    """
    class Meta:
        model = Message
        # Specifies the fields to include in the message form.
        fields = ['content']
        # Custom widget for the content field to use a textarea with limited rows.
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message here...'}),
        }
        # Removes the default label for the content field.
        labels = {
            'content': '',
        }

    def clean_content(self):
        """
        Validates that the message content is not empty or just whitespace.
        """
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise forms.ValidationError("Message cannot be empty.")
        return content
