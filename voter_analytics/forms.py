# voter_analytics/forms.py

from django import forms
import datetime

class FilterForm(forms.Form):
    PARTY_CHOICES = [
        ('All', 'All'),
        ('Democrat', 'Democrat'),
        ('Republican', 'Republican'),
        ('Independent', 'Independent'),
        # 根据实际数据添加更多选项
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
