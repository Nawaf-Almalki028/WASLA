from django.http import HttpRequest,HttpResponse
from django.shortcuts import render


def base_view(request:HttpRequest):


    return render(request, 'main/base.html' )

def home_view(request):
    
    
    return render(request, 'main/home.html')

def teams_view(request):
    
    
    return render(request, 'main/teams.html')


def hackathon_details_view(request):
    
    
    return render(request, 'main/hackathon_details.html')


def all_hackathons_view(request):
    
    
    return render(request, 'main/all_hackathons.html')

def pricing_view(request):
    
    
    return render(request, 'main/pricing.html')
