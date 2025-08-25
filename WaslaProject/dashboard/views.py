from django.shortcuts import render
from django.http import HttpRequest



def dashboard_home_view(request:HttpRequest):
    return render(request,'home.html')


def dashboard_add_hackathon_view(request:HttpRequest):
    return render(request, 'add_hackathon.html')



def dashboard_hackathon_details_view(request:HttpRequest, id:int):
    return render(request, 'hackathon_details.html')

def dashboard_hackathons_view(request:HttpRequest):
    return render(request, 'hackathons.html')

def dashboard_judges_view(request:HttpRequest):
    return render(request, 'judges.html')

def dashboard_teams_view(request:HttpRequest):
    return render(request, 'teams.html')



def dashboard_team_details_view(request:HttpRequest,id):
    return render(request, 'team_details.html')


def dashboard_admins_view(request:HttpRequest):
    return render(request, 'admins.html')


def dashboard_users_view(request:HttpRequest):
    return render(request, 'users.html')

def dashboard_settings_view(request:HttpRequest):
    return render(request, 'settings.html')


def dashboard_ai_feature_view(request:HttpRequest, hackathon_id):
    return render(request, 'ai_feature.html')