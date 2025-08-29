from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('base/', views.base_view, name="base_view"),
    path('', views.home_view, name='home_view'),
    path('hackathon_details/<hackathon_id>/', views.hackathon_details_view, name='hackathon_details_view'),
    path('all_hackathons/', views.all_hackathons_view, name='all_hackathons_view'),
    path('pricing/', views.pricing_view, name='pricing_view'),
    path('teams/', views.teams_view, name='teams_view'),
    path('create_team/', views.create_team_view, name='create_team_view'),



]