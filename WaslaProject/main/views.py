from datetime import timedelta
from django.http import HttpRequest,HttpResponse
from django.shortcuts import render
from django.utils.timezone import now
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
      
def all_hackathons_view(request):
    search_query = request.GET.get("search", "")
    location = request.GET.get("location", "all")
    time_filter = request.GET.get("time", "all")

    hackathons = Hackathon.objects.all()

    if search_query:
        hackathons = hackathons.filter(title__icontains=search_query)

    if location != "all":
        hackathons = hackathons.filter(location__iexact=location)

    if time_filter != "all":
        today = now().date()
        if time_filter == "≤7":
            hackathons = hackathons.filter(end_date__lte=today + timedelta(days=7))
        elif time_filter == "8-30":
            hackathons = hackathons.filter(end_date__gte=today + timedelta(days=8),
                                           end_date__lte=today + timedelta(days=30))
        elif time_filter == ">30":
            hackathons = hackathons.filter(end_date__gt=today + timedelta(days=30))

    locations = (
        Hackathon.objects.exclude(location__isnull=True)
        .exclude(location__exact="")
        .values_list("location", flat=True)
        .distinct()
        .order_by("location")
    )

    return render(request, "main/all_hackathons.html", {
        "hackathons": hackathons,
        "search_query": search_query,
        "location": location,
        "time_filter": time_filter,
        "locations": locations,
    })

def pricing_view(request):
    
    
    return render(request, 'main/pricing.html')
