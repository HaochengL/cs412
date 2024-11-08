from django.urls import path
from . import views

urlpatterns = [
    path('', views.VotersListView.as_view(), name='voters'),  # 首页显示Voter列表
    path('voter/<int:pk>/', views.VoterDetailView.as_view(), name='voter_detail'),  # Voter详细页
    path('graphs/', views.GraphsView.as_view(), name='graphs'),  # 图表页面
]