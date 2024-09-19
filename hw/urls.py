from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path(r'', views.home, name="home"), ##our first url
    path(r'about', views.about, name="about"),
]