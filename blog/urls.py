from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    #path(r'', views.home, name="home"), ##our first url
    path(r'', views.ShowAllView.as_view(), name="show_all"),
]