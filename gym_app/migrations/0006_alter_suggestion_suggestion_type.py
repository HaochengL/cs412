# Generated by Django 5.1.3 on 2024-12-04 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_app', '0005_friend'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggestion',
            name='suggestion_type',
            field=models.CharField(choices=[('Exercise', 'Exercise'), ('Diet', 'Diet'), ('bmi', 'BMI')], max_length=10),
        ),
    ]
