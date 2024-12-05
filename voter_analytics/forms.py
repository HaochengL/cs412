# voter_analytics/forms.py

from django import forms
import datetime

class FilterForm(forms.Form):
    PARTY_CHOICES = [
        ('All', 'All'),
        ('Democrat', 'Democrat'),
        ('Republican', 'Republican'),
        ('Unaffiliated', 'Unaffiliated'),
        ('Libertarian', 'Libertarian'),
        ('Green', 'Green'),
        ('Independent', 'Independent'),
        ('Socialist', 'Socialist'),
        ('Progressive', 'Progressive'),
        ('Other', 'Other'),
        # Add more options as needed based on your PARTY_MAP
    ]
    
    VOTER_SCORE_CHOICES = [
        ('All', 'All'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]
    
    ELECTION_CHOICES = [
        ('v20state', '2020 State Election'),
        ('v21town', '2021 Town Election'),
        ('v21primary', '2021 Primary Election'),
        ('v22general', '2022 General Election'),
        ('v23town', '2023 Town Election'),
    ]
    
    party_affiliation = forms.ChoiceField(
        choices=PARTY_CHOICES, 
        required=False, 
        label='Party Affiliation'
    )
    
    current_year = datetime.datetime.now().year
    YEAR_CHOICES = [(year, year) for year in range(1900, current_year + 1)]
    
    min_dob = forms.ChoiceField(
        choices=[('', 'Any')] + YEAR_CHOICES, 
        required=False, 
        label='Minimum Year of Birth'
    )
    
    max_dob = forms.ChoiceField(
        choices=[('', 'Any')] + YEAR_CHOICES, 
        required=False, 
        label='Maximum Year of Birth'
    )
    
    voter_score = forms.ChoiceField(
        choices=VOTER_SCORE_CHOICES, 
        required=False, 
        label='Voter Score'
    )
    
    elections = forms.MultipleChoiceField(
        choices=ELECTION_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Voted in Elections'
    )

class DataFilterForm(forms.Form):
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