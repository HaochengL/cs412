# gym_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, WorkoutSession, FitnessMetric, Suggestion, WorkoutType, Message

class RegistrationForm(UserCreationForm):
    """
    Extends the built-in UserCreationForm to include an email field.
    Used for registering new users.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class WorkoutSessionForm(forms.ModelForm):
    """
    Form for creating and updating WorkoutSession instances.
    Includes a customized date input widget for session_date.
    """
    class Meta:
        model = WorkoutSession
        fields = [
            'workout_type', 'session_date', 'session_duration_hours',
            'max_bpm', 'avg_bpm', 'resting_bpm'
        ]
        widgets = {
            'session_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ProfileForm(forms.ModelForm):
    """
    Form for creating and updating Profile instances.
    Includes an option to remove the current photo.
    """
    remove_photo = forms.BooleanField(required=False, label='Remove current photo')

    class Meta:
        model = Profile
        fields = ['age', 'gender', 'weight_kg', 'height_m', 'experience_level', 'photo', 'remove_photo']

    def save(self, commit=True):
        """
        Overrides the default save method to handle photo removal.
        If 'remove_photo' is checked, the existing photo is deleted.
        """
        profile = super().save(commit=False)
        if self.cleaned_data.get('remove_photo'):
            if profile.photo:
                profile.photo.delete(save=False)
            profile.photo = None
        if commit:
            profile.save()
        return profile

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and customizes the photo field's clear checkbox label.
        """
        super(ProfileForm, self).__init__(*args, **kwargs)
        # Removes the label for the clear checkbox to avoid displaying 'Clear' option
        self.fields['photo'].widget.clear_checkbox_label = ''


class FitnessMetricForm(forms.ModelForm):
    """
    Form for creating and updating FitnessMetric instances.
    """
    class Meta:
        model = FitnessMetric
        fields = ['fat_percentage', 'water_intake_liters']


class SuggestionForm(forms.ModelForm):
    """
    Form for creating and updating Suggestion instances.
    """
    class Meta:
        model = Suggestion
        fields = ['suggestion_type', 'suggestion_text']


class WorkoutTypeForm(forms.ModelForm):
    """
    Form for creating and updating WorkoutType instances.
    """
    class Meta:
        model = WorkoutType
        fields = ['name', 'description']


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

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        label='Gender',
        initial='All'
    )

    min_age = forms.IntegerField(
        required=False,
        label='Minimum Age'
    )

    max_age = forms.IntegerField(
        required=False,
        label='Maximum Age'
    )

    experience_level = forms.ChoiceField(
        choices=EXPERIENCE_LEVEL_CHOICES,
        required=False,
        label='Experience Level',
        initial='All'
    )

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
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'content': '',
        }
