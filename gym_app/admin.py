# gym_app/admin.py

from django.contrib import admin
from .models import (
    Profile, WorkoutType, WorkoutSession,
    FitnessMetric, Suggestion, Friend
)

# Register the Profile model to make it accessible in the Django admin interface.
admin.site.register(Profile)

# Register the WorkoutType model to manage different workout categories via admin.
admin.site.register(WorkoutType)

# Register the WorkoutSession model to handle user workout sessions in admin.
admin.site.register(WorkoutSession)

# Register the FitnessMetric model to track and manage fitness metrics through admin.
admin.site.register(FitnessMetric)

# Register the Suggestion model to store and view user-specific suggestions in admin.
admin.site.register(Suggestion)

# Register the Friend model to manage friendships between profiles in the admin panel.
admin.site.register(Friend)
