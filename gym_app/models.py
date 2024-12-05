# gym_app/models.py

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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    weight_kg = models.FloatField()
    height_m = models.FloatField()
    experience_level = models.IntegerField(choices=EXPERIENCE_LEVEL_CHOICES)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    # BMI will be calculated based on weight and height

    def add_friend(self, profile):
        """
        Adds a friendship between the current profile and another profile.
        """
        Friend.objects.get_or_create(profile=self, friend=profile)
        Friend.objects.get_or_create(profile=profile, friend=self)

    def remove_friend(self, profile):
        """
        Removes the friendship between the current profile and another profile.
        """
        Friend.objects.filter(profile=self, friend=profile).delete()
        Friend.objects.filter(profile=profile, friend=self).delete()

    def get_friends(self):
        """
        Retrieves a list of all friends associated with the current profile.
        """
        return [friendship.friend for friendship in self.friends.all()]

    def is_friend(self, profile):
        """
        Checks if the current profile is friends with another profile.
        """
        return Friend.objects.filter(profile=self, friend=profile).exists()
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def bmi(self):
        """
        Calculates and returns the Body Mass Index (BMI) for the profile.
        """
        if self.height_m > 0:
            return round(self.weight_kg / (self.height_m ** 2), 2)
        return None

    def get_absolute_url(self):
        """
        Returns the URL to access a detail view of this profile.
        """
        return reverse('profile_detail', kwargs={'pk': self.pk})

class WorkoutType(models.Model):
    """
    Defines different types of workouts.
    """
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class WorkoutSession(models.Model):
    """
    Represents a workout session conducted by a user.
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    workout_type = models.ForeignKey(WorkoutType, on_delete=models.SET_NULL, null=True)
    session_date = models.DateField()
    session_duration_hours = models.FloatField()
    calories_burned = models.PositiveIntegerField()
    max_bpm = models.PositiveIntegerField()
    avg_bpm = models.PositiveIntegerField()
    resting_bpm = models.PositiveIntegerField()

    def calculate_calories_burned(self):
        """
        Calculates the number of calories burned during the workout session based on various factors.
        """
        profile = self.profile
        age = profile.age
        weight = profile.weight_kg
        duration_min = self.session_duration_hours * 60
        avg_bpm = self.avg_bpm
        gender = profile.gender

        if gender == 'Male':
            calories = ((-55.0969 + (0.6309 * avg_bpm) + (0.1988 * weight) + (0.2017 * age)) * duration_min) / 4.184
        elif gender == 'Female':
            calories = ((-20.4022 + (0.4472 * avg_bpm) - (0.1263 * weight) + (0.074 * age)) * duration_min) / 4.184
        else:
            # For 'Other', use the average of male and female formulas
            male_calories = ((-55.0969 + (0.6309 * avg_bpm) + (0.1988 * weight) + (0.2017 * age)) * duration_min) / 4.184
            female_calories = ((-20.4022 + (0.4472 * avg_bpm) - (0.1263 * weight) + (0.074 * age)) * duration_min) / 4.184
            calories = (male_calories + female_calories) / 2

        # Ensure calories are not negative
        calories = max(0, calories)
        return int(calories)

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically calculate and set calories_burned before saving.
        """
        self.calories_burned = self.calculate_calories_burned()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profile.user.username}'s {self.workout_type.name} on {self.session_date}"

    def get_absolute_url(self):
        """
        Returns the URL to access a detail view of this workout session.
        """
        return reverse('workoutsession_detail', kwargs={'pk': self.pk})

class FitnessMetric(models.Model):
    """
    Records fitness metrics over time.
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date_recorded = models.DateField(auto_now_add=True)
    fat_percentage = models.FloatField()
    water_intake_liters = models.FloatField()

    def __str__(self):
        return f"{self.profile.user.username}'s Metrics on {self.date_recorded}"

    def get_absolute_url(self):
        """
        Returns the URL to access a detail view of these fitness metrics.
        """
        return reverse('fitnessmetric_detail', kwargs={'pk': self.pk})

class Suggestion(models.Model):
    """
    Stores suggestions related to exercise, diet, or BMI for a user.
    """
    SUGGESTION_TYPE_CHOICES = [
        ('Exercise', 'Exercise'),
        ('Diet', 'Diet'),
        ('bmi', 'BMI'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    suggestion_text = models.TextField()
    suggestion_type = models.CharField(max_length=10, choices=SUGGESTION_TYPE_CHOICES)
    title = models.CharField(max_length=50, default='General')

    def __str__(self):
        return f"{self.title} Suggestion for {self.profile.user.username}"

    def get_absolute_url(self):
        """
        Returns the URL to access a detail view of this suggestion.
        """
        return reverse('suggestion_detail', kwargs={'pk': self.pk})

# -----------------------------------
# Additional Models and Functions
# -----------------------------------

class MemberData(models.Model):
    """
    Represents comprehensive member data for analytics purposes.
    """
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    weight_kg = models.FloatField()
    height_m = models.FloatField()
    max_bpm = models.IntegerField()
    avg_bpm = models.IntegerField()
    resting_bpm = models.IntegerField()
    session_duration_hours = models.FloatField()
    calories_burned = models.FloatField()
    workout_type = models.CharField(max_length=50)
    fat_percentage = models.FloatField()
    water_intake_liters = models.FloatField()
    workout_frequency = models.IntegerField()  # days per week
    experience_level = models.IntegerField()
    bmi = models.FloatField()

    def __str__(self):
        return f'{self.gender} aged {self.age}'

def load_member_data_from_csv():
    """
    Loads member data from a CSV file into the MemberData model.
    """
    # First, delete existing records to avoid duplication
    MemberData.objects.all().delete()

    # Construct the path to the CSV file
    data_file = os.path.join(settings.BASE_DIR, 'gym_app', 'data', 'gym_members_exercise_tracking.csv')

    with open(data_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
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
                member_data.save()
            except Exception as e:
                print(f"Error processing row: {row}")
                print(e)

class Friend(models.Model):
    """
    Represents a friendship between two profiles.
    """
    profile = models.ForeignKey(
        'Profile', related_name='friends', on_delete=models.CASCADE
    )
    friend = models.ForeignKey(
        'Profile', related_name='friend_of', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'friend')  # Ensures unique friendships

    def __str__(self):
        return f"{self.profile.user.username} is friends with {self.friend.user.username}"
    

class Message(models.Model):
    """
    Represents a message sent from one user to another.
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['-timestamp']  # Orders messages by most recent first

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username} at {self.timestamp}"
