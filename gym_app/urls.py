# gym_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Home
    path('', views.HomeView.as_view(), name='home'),

    # Profile URLs
    path('profile/create/', views.ProfileCreateView.as_view(), name='profile_create'),
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/<int:pk>/update/', views.ProfileUpdateView.as_view(), name='profile_update'),

    # Workout Sessions URLs
    path('workout_sessions/', views.WorkoutSessionListView.as_view(), name='workoutsession_list'),
    path('workout_session/add/', views.WorkoutSessionCreateView.as_view(), name='workoutsession_add'),
    path('workout_session/<int:pk>/', views.WorkoutSessionDetailView.as_view(), name='workoutsession_detail'),
    path('workout_session/<int:pk>/update/', views.WorkoutSessionUpdateView.as_view(), name='workoutsession_update'),
    path('workout_session/<int:pk>/delete/', views.WorkoutSessionDeleteView.as_view(), name='workoutsession_delete'),

    # Workout Types URLs
    path('workout_type/add/', views.WorkoutTypeCreateView.as_view(), name='workouttype_add'),
    path('workout_types/', views.WorkoutTypeListView.as_view(), name='workouttype_list'),

    # Fitness Metrics URLs
    path('fitness_metric/add/', views.FitnessMetricCreateView.as_view(), name='fitnessmetric_add'),
    path('fitness_metric/update/', views.FitnessMetricUpdateView.as_view(), name='fitnessmetric_update'),
    path('fitness_metric/delete/<int:pk>/', views.FitnessMetricDeleteView.as_view(), name='fitnessmetric_delete'),

    # Suggestions URLs
    path('suggestions/', views.SuggestionListView.as_view(), name='suggestion_list'),

    # Friends URLs
    path('friends/', views.FriendListView.as_view(), name='friend_list'),
    path('friends/add/', views.AddFriendListView.as_view(), name='add_friend_list'),
    path('add_friend/<int:pk>/', views.AddFriendView.as_view(), name='add_friend'),
    path('remove_friend/<int:pk>/', views.RemoveFriendView.as_view(), name='remove_friend'),

    # Messaging URLs
    path('messages/send/<int:recipient_id>/', views.send_message, name='send_message'),
    path('messages/thread/<int:user_id>/', views.message_thread, name='message_thread'),
    path('messages/delete/<int:message_id>/', views.delete_message, name='delete_message'),
    path('messages/update/<int:message_id>/', views.update_message, name='update_message'),
    path('chat/', views.ChatListView.as_view(), name='chat'),
]
