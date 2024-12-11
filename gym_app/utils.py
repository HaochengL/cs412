# gym_app/utils.py
# Author: Haocheng Liu <easonlhc@bu.edu>
# Description: This file contains utility functions used across the gym_app, including suggestion generation.

def generate_suggestions(profile):
    suggestions = []
    
    # 获取用户的 BMI
    bmi = profile.bmi

    # 获取用户最新的健康指标
    latest_metric = profile.fitnessmetric_set.order_by('-date_recorded').first()
    if latest_metric:
        fat_percentage = latest_metric.fat_percentage
        water_intake = latest_metric.water_intake_liters
    else:
        fat_percentage = None
        water_intake = None

    # 获取过去一周的锻炼次数
    from django.utils import timezone
    from datetime import timedelta

    one_week_ago = timezone.now().date() - timedelta(days=7)
    recent_sessions = profile.workoutsession_set.filter(session_date__gte=one_week_ago).count()

    # 基于 BMI 生成建议
    if bmi:
        if bmi < 18.5:
            suggestions.append({
                'type': 'Diet',
                'text': 'Your BMI is low. It is recommended to increase your calorie intake, especially foods rich in protein and carbohydrates, to help gain weight.',
                'title': 'BMI'
            })
        elif 18.5 <= bmi < 24.9:
            suggestions.append({
                'type': 'Exercise',
                'text': 'Your BMI is within the normal range. Continue maintaining a healthy diet and regular exercise routine.',
                'title': 'BMI'
            })
        elif 25 <= bmi < 29.9:
            suggestions.append({
                'type': 'Diet',
                'text': 'Your BMI is slightly high. It is recommended to reduce the intake of high-calorie foods, increase the proportion of vegetables and fruits, and combine with regular exercise to aid weight loss.',
                'title': 'BMI'
            })
        else:
            suggestions.append({
                'type': 'Diet',
                'text': 'Your BMI is high. It is strongly recommended to consult a nutritionist and develop a personalized diet plan, combined with a professional exercise program to manage your weight.',
                'title': 'BMI'
            })

    # 基于水摄入量生成建议
    if water_intake is not None:
        if water_intake < 2.0:
            suggestions.append({
                'type': 'Diet',
                'text': 'Your daily water intake is low. It is recommended to drink at least 2 liters of water daily to maintain proper hydration.',
                'title': 'Water Intake'
            })
        elif 2.0 <= water_intake <= 3.0:
            suggestions.append({
                'type': 'Diet',
                'text': 'Your daily water intake is good. Continue maintaining this habit.',
                'title': 'Water Intake'
            })
        else:
            suggestions.append({
                'type': 'Diet',
                'text': 'Your daily water intake is high. Maintaining adequate hydration is beneficial for your health.',
                'title': 'Water Intake'
            })

    # 基于锻炼次数生成建议
    if recent_sessions < 3:
        suggestions.append({
            'type': 'Exercise',
            'text': f'You have completed {recent_sessions} Workout Sessions in the past week. It is recommended to exercise at least 3 times a week to maintain good health.',
            'title': 'Workout Sessions'
        })
    else:
        suggestions.append({
            'type': 'Exercise',
            'text': f'Great job! You have completed {recent_sessions} Workout Sessions in the past week. Keep up the regular exercise routine.',
            'title': 'Workout Sessions'
        })

    return suggestions
