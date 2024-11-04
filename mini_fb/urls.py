# mini_fb/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views  # Import Django's built-in authentication views
from .views import (
    ShowAllProfilesView,
    ShowProfilePageView,
    CreateProfileView,
    CreateStatusMessageView,
    UpdateProfileView,
    DeleteStatusMessageView,
    UpdateStatusMessageView,
    CreateFriendView,
    ShowFriendSuggestionsView,
    ShowNewsFeedView,
)

urlpatterns = [
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'),
    path('profile/<int:pk>/', ShowProfilePageView.as_view(), name='show_profile'),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),

    # 修改 URL 模式以匹配测试期望
    path('status/create_status/', CreateStatusMessageView.as_view(), name='status/create_status'),
    path('profile/update/', UpdateProfileView.as_view(), name='profile/update'),
    path('status/<int:pk>/update/', UpdateStatusMessageView.as_view(), name='update_status'),
    path('status/<int:pk>/delete/', DeleteStatusMessageView.as_view(), name='delete_status'),
    path('profile/add_friend/<int:other_pk>/', CreateFriendView.as_view(), name='profile/add_friend'),
    path('profile/friend_suggestions/', ShowFriendSuggestionsView.as_view(), name='profile/friend_suggestions'),
    path('profile/news_feed/', ShowNewsFeedView.as_view(), name='profile/news_feed'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='mini_fb/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='mini_fb/logged_out.html'), name='logout'),
]
