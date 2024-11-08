from django.db import models

# Create your models here.
# voter_analytics/models.py

import csv
import datetime
from django.db import models

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
    # 删除现有记录以防止重复
    Voter.objects.all().delete()
    
    filename = 'voter_analytics/data/newton_voters.csv'  # 确保CSV文件路径正确
    voters = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # 解析日期
                date_of_birth = datetime.datetime.strptime(row['Date of Birth'], '%Y-%m-%d').date()
                date_of_registration = datetime.datetime.strptime(row['Date of Registration'], '%Y-%m-%d').date()
                
                # 解析布尔值字段
                def parse_boolean(value):
                    return value.strip().upper() == 'TRUE'
                
                voter = Voter(
                    last_name=row['Last Name'],
                    first_name=row['First Name'],
                    residential_address_street_number=row['Residential Address - Street Number'],
                    residential_address_street_name=row['Residential Address - Street Name'],
                    residential_address_apartment_number=row['Residential Address - Apartment Number'] or None,
                    residential_address_zip_code=row['Residential Address - Zip Code'],
                    date_of_birth=date_of_birth,
                    date_of_registration=date_of_registration,
                    party_affiliation=row['Party Affiliation'].strip(),
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
    
    # 批量创建
    Voter.objects.bulk_create(voters)
    print(f'Done. Created {Voter.objects.count()} Voter records.')
