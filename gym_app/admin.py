# gym_app/admin.py

from django.contrib import admin
from .models import (
    Profile, WorkoutType, WorkoutSession,
    FitnessMetric, Suggestion, Friend 
)

admin.site.register(Profile)
admin.site.register(WorkoutType)
admin.site.register(WorkoutSession)
admin.site.register(FitnessMetric)
admin.site.register(Suggestion)
admin.site.register(Friend) 
