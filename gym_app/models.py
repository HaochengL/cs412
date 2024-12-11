# gym_app/models.py
# Author: Haocheng Liu <easonlhc@bu.edu>
# Description: This file defines the Django models for profiles, workout types, workout sessions,
#              fitness metrics, suggestions, member data for analytics, friendships, and messaging.

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import csv
import os
from django.conf import settings

class Profile(models.Model):
    """
    Extends the built-in User model to include fitness-related data.
    """
    EXPERIENCE_LEVEL_CHOICES = [
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
    ]

    # One-to-one relationship linking this Profile to a specific User from the Django auth system.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Age of the user in whole years.
    age = models.PositiveIntegerField()
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    # Gender of the user with predefined choices.
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    # Weight in kilograms (float allows decimal values for more precision).
    weight_kg = models.FloatField()
    # Height in meters. Similarly stored as float for precision in BMI calculation.
    height_m = models.FloatField()
    # Stores experience level as an integer key from EXPERIENCE_LEVEL_CHOICES.
    experience_level = models.IntegerField(choices=EXPERIENCE_LEVEL_CHOICES)
    # An optional profile photo. Null and blank allowed for users with no photo.
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    # BMI will be calculated based on weight and height.

    def add_friend(self, profile):
        """
        Adds a friendship between the current profile and another profile.
        Creates reciprocal Friend objects for mutual friendship.
        """
        Friend.objects.get_or_create(profile=self, friend=profile)
        Friend.objects.get_or_create(profile=profile, friend=self)

    def remove_friend(self, profile):
        """
        Removes the friendship between the current profile and another profile.
        Deletes both reciprocal Friend objects.
        """
        Friend.objects.filter(profile=self, friend=profile).delete()
        Friend.objects.filter(profile=profile, friend=self).delete()

    def get_friends(self):
        """
        Retrieves a list of all friends associated with the current profile.
        Returns a list of Profile instances.
        """
        return [friendship.friend for friendship in self.friends.all()]

    def is_friend(self, profile):
        """
        Checks if the current profile is friends with another profile.
        Returns True if a friendship exists, False otherwise.
        """
        return Friend.objects.filter(profile=self, friend=profile).exists()
    
    def __str__(self):
        """
        Returns a human-readable representation of the Profile, typically the user's username.
        """
        return f"{self.user.username}'s Profile"

    @property
    def bmi(self):
        """
        Calculates and returns the Body Mass Index (BMI) for the profile.
        Returns None if height is zero to avoid division by zero errors.
        """
        if self.height_m > 0:
            return round(self.weight_kg / (self.height_m ** 2), 2)
        return None

    def get_absolute_url(self):
        """
        Provides the URL to access a detailed view of this profile.
        Useful for redirects after creating or updating a profile.
        """
        return reverse('profile_detail', kwargs={'pk': self.pk})


class WorkoutType(models.Model):
    """
    Defines different types of workouts.
    Examples include Cardio, Strength Training, Yoga, etc.
    """
    # Name of the workout type (e.g., Cardio, Strength Training).
    name = models.CharField(max_length=50)
    # Optional description providing more details about the workout type.
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        """
        Returns the name of the workout type for easy identification.
        """
        return self.name


class WorkoutSession(models.Model):
    """
    Represents a workout session conducted by a user.
    Tracks details like workout type, duration, calories burned, and heart rates.
    """
    # ForeignKey linking the session to the user's profile.
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    # ForeignKey linking to the type of workout performed.
    workout_type = models.ForeignKey(WorkoutType, on_delete=models.SET_NULL, null=True)
    # Date when the workout session took place.
    session_date = models.DateField()
    # Duration of the workout session in hours.
    session_duration_hours = models.FloatField()
    # Number of calories burned during the session.
    calories_burned = models.PositiveIntegerField()
    # Maximum beats per minute recorded during the session.
    max_bpm = models.PositiveIntegerField()
    # Average beats per minute during the session.
    avg_bpm = models.PositiveIntegerField()
    # Resting beats per minute before the session.
    resting_bpm = models.PositiveIntegerField()

    def calculate_calories_burned(self):
        """
        Calculates the number of calories burned during the workout session based on various factors.
        Factors include age, weight, duration, average BPM, and gender.
        Returns the calculated calories as an integer.
        Ensures that calories are not negative.
        """
        profile = self.profile
        age = profile.age
        weight = profile.weight_kg
        duration_min = self.session_duration_hours * 60  # Convert hours to minutes.
        avg_bpm = self.avg_bpm
        gender = profile.gender

        if gender == 'Male':
            # Formula for males to calculate calories burned.
            calories = ((-55.0969 + (0.6309 * avg_bpm) + (0.1988 * weight) + (0.2017 * age)) * duration_min) / 4.184
        elif gender == 'Female':
            # Formula for females to calculate calories burned.
            calories = ((-20.4022 + (0.4472 * avg_bpm) - (0.1263 * weight) + (0.074 * age)) * duration_min) / 4.184
        else:
            # For 'Other' gender, use the average of male and female formulas.
            male_calories = ((-55.0969 + (0.6309 * avg_bpm) + (0.1988 * weight) + (0.2017 * age)) * duration_min) / 4.184
            female_calories = ((-20.4022 + (0.4472 * avg_bpm) - (0.1263 * weight) + (0.074 * age)) * duration_min) / 4.184
            calories = (male_calories + female_calories) / 2

        # Ensure calories are not negative.
        calories = max(0, calories)
        return int(calories)

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically calculate and set calories_burned before saving.
        """
        self.calories_burned = self.calculate_calories_burned()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a string representation of the workout session, including the user's name, workout type, and date.
        """
        return f"{self.profile.user.username}'s {self.workout_type.name} on {self.session_date}"

    def get_absolute_url(self):
        """
        Provides the URL to access a detailed view of this workout session.
        Useful for redirects after creating or updating a session.
        """
        return reverse('workoutsession_detail', kwargs={'pk': self.pk})


class FitnessMetric(models.Model):
    """
    Records fitness metrics over time for each user.
    Metrics include fat percentage and water intake.
    """
    # ForeignKey linking the metric to the user's profile.
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    # Automatically sets the date when the metric was recorded.
    date_recorded = models.DateField(auto_now_add=True)
    # User's body fat percentage.
    fat_percentage = models.FloatField()
    # Amount of water intake in liters.
    water_intake_liters = models.FloatField()

    def __str__(self):
        """
        Returns a string representation of the fitness metric, including the user's name and the date recorded.
        """
        return f"{self.profile.user.username}'s Metrics on {self.date_recorded}"

    def get_absolute_url(self):
        """
        Provides the URL to access a detailed view of these fitness metrics.
        Useful for redirects after creating or updating a metric.
        """
        return reverse('fitnessmetric_detail', kwargs={'pk': self.pk})


class Suggestion(models.Model):
    """
    Stores suggestions related to exercise, diet, or BMI for a user.
    Suggestions are auto-generated based on user data.
    """
    SUGGESTION_TYPE_CHOICES = [
        ('Exercise', 'Exercise'),
        ('Diet', 'Diet'),
        ('bmi', 'BMI'),
    ]

    # ForeignKey linking the suggestion to the user's profile.
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    # Automatically sets the date when the suggestion was created.
    date_created = models.DateField(auto_now_add=True)
    # Text content of the suggestion.
    suggestion_text = models.TextField()
    # Type of suggestion (Exercise, Diet, or BMI).
    suggestion_type = models.CharField(max_length=10, choices=SUGGESTION_TYPE_CHOICES)
    # Title of the suggestion, defaulting to 'General' if not specified.
    title = models.CharField(max_length=50, default='General')

    def __str__(self):
        """
        Returns a string representation of the suggestion, including the title and the user's name.
        """
        return f"{self.title} Suggestion for {self.profile.user.username}"

    def get_absolute_url(self):
        """
        Provides the URL to access a detailed view of this suggestion.
        Useful for redirects after creating or updating a suggestion.
        """
        return reverse('suggestion_detail', kwargs={'pk': self.pk})


# -----------------------------------
# Additional Models and Functions
# -----------------------------------

class MemberData(models.Model):
    """
    Represents comprehensive member data for analytics purposes.
    This model is used to load and analyze data from external CSV sources.
    """
    # Age of the member.
    age = models.IntegerField()
    # Gender of the member.
    gender = models.CharField(max_length=10)
    # Weight in kilograms.
    weight_kg = models.FloatField()
    # Height in meters.
    height_m = models.FloatField()
    # Maximum BPM during workout.
    max_bpm = models.IntegerField()
    # Average BPM during workout.
    avg_bpm = models.IntegerField()
    # Resting BPM before workout.
    resting_bpm = models.IntegerField()
    # Duration of workout session in hours.
    session_duration_hours = models.FloatField()
    # Calories burned during workout.
    calories_burned = models.FloatField()
    # Type of workout performed.
    workout_type = models.CharField(max_length=50)
    # Body fat percentage.
    fat_percentage = models.FloatField()
    # Water intake in liters.
    water_intake_liters = models.FloatField()
    # Frequency of workouts per week.
    workout_frequency = models.IntegerField()  # days per week
    # Experience level of the member.
    experience_level = models.IntegerField()
    # Body Mass Index.
    bmi = models.FloatField()

    def __str__(self):
        """
        Returns a string representation of the member data, including gender and age.
        """
        return f'{self.gender} aged {self.age}'


def load_member_data_from_csv():
    """
    Loads member data from a CSV file into the MemberData model.
    This function reads a CSV file located in the gym_app/data directory and populates the MemberData table.
    It first clears existing data to avoid duplication.
    """
    # First, delete existing records to avoid duplication.
    MemberData.objects.all().delete()

    # Construct the path to the CSV file.
    data_file = os.path.join(settings.BASE_DIR, 'gym_app', 'data', 'gym_members_exercise_tracking.csv')

    # Open and read the CSV file.
    with open(data_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Create a new MemberData instance with data from the CSV row.
                member_data = MemberData(
                    age=int(row['Age']),
                    gender=row['Gender'],
                    weight_kg=float(row['Weight (kg)']),
                    height_m=float(row['Height (m)']),
                    max_bpm=int(row['Max_BPM']),
                    avg_bpm=int(row['Avg_BPM']),
                    resting_bpm=int(row['Resting_BPM']),
                    session_duration_hours=float(row['Session_Duration (hours)']),
                    calories_burned=float(row['Calories_Burned']),
                    workout_type=row['Workout_Type'],
                    fat_percentage=float(row['Fat_Percentage']),
                    water_intake_liters=float(row['Water_Intake (liters)']),
                    workout_frequency=int(row['Workout_Frequency (days/week)']),
                    experience_level=int(row['Experience_Level']),
                    bmi=float(row['BMI']),
                )
                member_data.save()  # Save the instance to the database.
            except Exception as e:
                # Print error message for any row that fails to process.
                print(f"Error processing row: {row}")
                print(e)


class Friend(models.Model):
    """
    Represents a friendship between two profiles.
    Ensures that friendships are unique and mutual.
    """
    # ForeignKey linking to the Profile initiating the friendship.
    profile = models.ForeignKey(
        'Profile', related_name='friends', on_delete=models.CASCADE
    )
    # ForeignKey linking to the Profile being friended.
    friend = models.ForeignKey(
        'Profile', related_name='friend_of', on_delete=models.CASCADE
    )
    # Timestamp when the friendship was created.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures that each friendship pair is unique, preventing duplicate friendships.
        unique_together = ('profile', 'friend')  # Ensures unique friendships

    def __str__(self):
        """
        Returns a string representation of the friendship between two users.
        """
        return f"{self.profile.user.username} is friends with {self.friend.user.username}"


class Message(models.Model):
    """
    Represents a message sent from one user to another.
    Supports threaded conversations through the parent field.
    """
    # ForeignKey linking to the User who sent the message.
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    # ForeignKey linking to the User who received the message.
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    # Content of the message.
    content = models.TextField()
    # Timestamp when the message was sent.
    timestamp = models.DateTimeField(auto_now_add=True)
    # Self-referential ForeignKey to allow threaded (reply) messages.
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        # Orders messages by most recent first.
        ordering = ['-timestamp']  # Orders messages by most recent first

    def __str__(self):
        """
        Returns a string representation of the message, including sender, recipient, and timestamp.
        """
        return f"From {self.sender.username} to {self.recipient.username} at {self.timestamp}"
