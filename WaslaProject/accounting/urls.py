from django.contrib import admin
from django.urls import path,include
from . import views

app_name = "accounting"

urlpatterns = [
    path('signin/', views.accounting_signin, name='accounting_signin'),
    path('signup/', views.accounting_signup, name='accounting_signup'),
    path('<str:username>/profile/', views.accounting_profile, name='accounting_profile'),
    path('edit_profile/', views.accounting_edit_profile, name='accounting_edit_profile'),
    path('logout/', views.accounting_logout, name='accounting_logout'),
    path('', views.accounting_account, name='accounting_account'),
    path('skills_bio/', views.accounting_skills_bio, name='accounting_skills_bio'),
    path('social_links/', views.accounting_social_links, name='accounting_social_links'),
    path('security/', views.accounting_security, name='accounting_security'),
    path('hackathons/', views.accounting_hackathons, name='accounting_hackathons'),
    path('teams/', views.accounting_teams, name='accounting_teams'),
    path('create_team/<int:hackathon_id>', views.accounting_create_team, name='accounting_create_team'),
    path('team_page/<int:hackathon_id>', views.accounting_team_page, name='accounting_team_page'),
    path('team_request/<int:team_id>/join/', views.accounting_team_request, name='accounting_team_request'),
    
]

