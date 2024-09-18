from django.urls import path
from . import views

urlpatterns = [
    path('', views.quote, name='quote'),  # Main page
    path('quote/', views.quote, name='quote'),  # Same as main page
    path('show_all/', views.show_all, name='show_all'),  # Show all quotes and images
    path('about/', views.about, name='about'),  # About page
]
