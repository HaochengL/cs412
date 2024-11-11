# voter_analytics/models.py

import csv
import datetime
import os
from django.db import models
from django.conf import settings

# Mapping from party codes to full party names
PARTY_MAP = {
    'D': 'Democrat',
    'R': 'Republican',
    'U': 'Unaffiliated',
    'L': 'Libertarian',
    'G': 'Green',
    'J': 'Junk',
    'A': 'Alliance',
    'CC': 'Citizens Choice',
    'X': 'Independent',
    'Q': 'Quadripart',
    'S': 'Socialist',
    'FF': 'Freedom Fighters',
    'HH': 'Heritage',
    'T': 'Tea Party',
    'AA': 'American Alliance',
    'GG': 'Grassroots',
    'Z': 'Zero Party',
    'O': 'Other',
    'P': 'Progressive',
    'E': 'Environmentalist',
    'V': 'Veteran',
    'H': 'Humanitarian',
    'Y': 'Youth',
    'W': 'Workers',
    'EE': 'Eco-Efficient',
    'K': 'Knowledgeable',
    # Add any other necessary mappings
}

class Voter(models.Model):
    """
    Represents a registered voter in Newton, MA.
    """
    # Identification
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    residential_address_street_number = models.CharField(max_length=10)
    residential_address_street_name = models.CharField(max_length=100)
    residential_address_apartment_number = models.CharField(max_length=10, blank=True, null=True)
    residential_address_zip_code = models.CharField(max_length=10)
    
    # Dates
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    
    # Party and Precinct
    party_affiliation = models.CharField(max_length=50)
    precinct_number = models.CharField(max_length=10)
    
    # Election Participation
    v20state = models.BooleanField(default=False)
    v21town = models.BooleanField(default=False)
    v21primary = models.BooleanField(default=False)
    v22general = models.BooleanField(default=False)
    v23town = models.BooleanField(default=False)
    
    # Voter Score
    voter_score = models.IntegerField()
    
    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.residential_address_street_number} {self.residential_address_street_name}, {self.residential_address_zip_code})'

def load_data():
    """
    Load voter data from a CSV file into the Voter model.
    """
    # Delete existing records to prevent duplicates
    Voter.objects.all().delete()
    
    # Build the absolute path to the CSV file
    filename = os.path.join(settings.BASE_DIR, 'voter_analytics', 'data', 'newton_voters.csv')
    
    voters = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Parse dates
                date_of_birth = datetime.datetime.strptime(row['Date of Birth'], '%Y-%m-%d').date()
                date_of_registration = datetime.datetime.strptime(row['Date of Registration'], '%Y-%m-%d').date()
                
                # Parse boolean fields
                def parse_boolean(value):
                    return value.strip().upper() == 'TRUE'
                
                # Clean and standardize party name
                raw_party_code = row['Party Affiliation']
                party_code = raw_party_code.strip().upper()
                party_affiliation = PARTY_MAP.get(party_code, 'Other')  # Default to 'Other' if mapping not found

                # Create the Voter instance with the mapped full party name
                voter = Voter(
                    last_name=row['Last Name'].strip(),
                    first_name=row['First Name'].strip(),
                    residential_address_street_number=row['Residential Address - Street Number'].strip(),
                    residential_address_street_name=row['Residential Address - Street Name'].strip(),
                    residential_address_apartment_number=row['Residential Address - Apartment Number'].strip() or None,
                    residential_address_zip_code=row['Residential Address - Zip Code'].strip(),
                    date_of_birth=date_of_birth,
                    date_of_registration=date_of_registration,
                    party_affiliation=party_affiliation,  # Use the mapped full name here
                    precinct_number=row['Precinct Number'].strip(),
                    v20state=parse_boolean(row['v20state']),
                    v21town=parse_boolean(row['v21town']),
                    v21primary=parse_boolean(row['v21primary']),
                    v22general=parse_boolean(row['v22general']),
                    v23town=parse_boolean(row['v23town']),
                    voter_score=int(row['voter_score'])
                )
                voters.append(voter)
            except Exception as e:
                print(f"Skipped row due to error: {e}")
    
    # Bulk create the Voter instances
    Voter.objects.bulk_create(voters)
    print(f'Done. Created {Voter.objects.count()} Voter records.')
