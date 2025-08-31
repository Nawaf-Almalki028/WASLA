from django.http import HttpRequest,HttpResponse
from django.shortcuts import render

from dashboard.models import Hackathon, HackathonPrizes, Judge


def base_view(request:HttpRequest):


    return render(request, 'main/base.html' )

def home_view(request):
    hackathons = Hackathon.objects.all() 
    return render(request, 'main/home.html', {'hackathons': hackathons})
def teams_view(request):
    
    
    return render(request, 'main/teams.html')

def create_team_view(request):
    
    
    return render(request, 'main/create_team.html')


def hackathon_details_view(request , hackathon_id:int ):
    
    hackathon = Hackathon.objects.get(pk=hackathon_id)
    judges = Judge.objects.filter(hackathon_id=hackathon_id)
    prizes = HackathonPrizes.objects.filter(hackathon=hackathon).order_by("id")

    return render(request, 'main/hackathon_details.html', {
        "hackathon" : hackathon , 
        "judges" : judges , 
        "prizes" : prizes 
        })




def all_hackathons_view(request):
    hackathons = Hackathon.objects.all() 
  
    return render(request, 'main/all_hackathons.html', {'hackathons': hackathons})
      

def pricing_view(request):
    
    
    return render(request, 'main/pricing.html')
