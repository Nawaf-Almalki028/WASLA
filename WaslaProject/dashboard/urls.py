from django.urls import path
from . import views

app_name="dashboard"


urlpatterns = [
    path('', views.dashboard_home_view, name="dashboard_home_view"),
    path('add_hackathon/<str:type>', views.dashboard_add_hackathon_view, name="dashboard_add_hackathon_view"),
    path('hackathon_details/<id>/', views.dashboard_hackathon_details_view, name="dashboard_hackathon_details_view"),
    path('team_details/<id>/', views.dashboard_team_details_view, name="dashboard_team_details_view"),
    path('hackathons/', views.dashboard_hackathons_view, name="dashboard_hackathons_view"),
    path('judges/', views.dashboard_judges_view, name="dashboard_judges_view"),
    path('teams/', views.dashboard_teams_view, name="dashboard_teams_view"),
    path('admins/', views.dashboard_admins_view, name="dashboard_admins_view"),
    path('users/', views.dashboard_users_view, name="dashboard_users_view"),
    path('settings/', views.dashboard_settings_view, name="dashboard_settings_view"),
    path('ai_feature/<hackathon_id>', views.dashboard_ai_feature_view, name="dashboard_ai_feature_view"),
]