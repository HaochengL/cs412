# gym_app/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WorkoutSession, FitnessMetric, Suggestion
from .utils import generate_suggestions

@receiver(post_save, sender=WorkoutSession)
def create_suggestions_on_workout_session(sender, instance, created, **kwargs):
    if created:
        profile = instance.profile
        # Delete existing suggestions
        Suggestion.objects.filter(profile=profile).delete()
        # Generate new suggestions
        suggestions = generate_suggestions(profile)
        # Create new suggestion instances
        for sug in suggestions:
            Suggestion.objects.create(
                profile=profile,
                suggestion_type=sug['type'],
                suggestion_text=sug['text'],
                title=sug['title']
            )

@receiver(post_save, sender=FitnessMetric)
def create_suggestions_on_fitness_metric(sender, instance, created, **kwargs):
    if created:
        profile = instance.profile
        # Delete existing suggestions
        Suggestion.objects.filter(profile=profile).delete()
        # Generate new suggestions
        suggestions = generate_suggestions(profile)
        # Create new suggestion instances
        for sug in suggestions:
            Suggestion.objects.create(
                profile=profile,
                suggestion_type=sug['type'],
                suggestion_text=sug['text'],
                title=sug['title']
            )
