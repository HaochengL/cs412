from django.urls import path
from .views import * # our view class definition 
urlpatterns = [
    # map the URL (empty string) to the view
    path('', RandomArticleView.as_view(), name='random'), ## new
    path('show_all', ShowAllView.as_view(), name='show_all'), ## refactored
]