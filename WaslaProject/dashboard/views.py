import json
import re
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpRequest,Http404, JsonResponse
from WaslaProject import settings
from . import forms, models
from dotenv import load_dotenv
import os 
import requests
import base64
from django.utils.timezone import now
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Case, When, Value, CharField,Count,Q,Sum,Avg
from django.db import transaction
from django.db.models import Count
from django.core.paginator import Paginator
import google.generativeai as genai



load_dotenv()

PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel('gemini-2.0-flash')


def dashboard_home_view(request:HttpRequest):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    teams_per_day = (
        models.Team.objects
        .filter(hackathon__organization=request.user)
        .values('created_at__date')
        .annotate(count=Count('id'))
        .order_by('created_at__date')
    )

    line_labels = [str(item['created_at__date']) for item in teams_per_day]
    line_data = [item['count'] for item in teams_per_day]

    labels = []
    data = []
    chart_labels = []   
    chart_data = []
    hackathons = models.Hackathon.objects.filter(Q(organization=request.user))
    for hackathon in hackathons:
            labels.append(hackathon.title)
            total_members = sum(team.team_members.count() for team in hackathon.hackathon_team.all())
            data.append(total_members)
            stages = hackathon.hackathon_stage.order_by('id')
            total_stages = stages.count()
            if total_stages == 0:
                continue

            current_index = 0
            if hackathon.current_stage:
                for i, stage in enumerate(stages):
                    if stage.id == hackathon.current_stage.id:
                        current_index = i + 1  
                        break

            progress_percent = (current_index / total_stages) * 100
            chart_labels.append(hackathon.title)
            chart_data.append(progress_percent)

    analysis_data = {
        "active_hackathons": hackathons.filter(~Q(status=models.HackathonStatusChoices.FINISHED)).count(),
        "total_teams":  sum(h.hackathon_team.count() for h in hackathons),
        "total_participants": sum(sum(t.team_members.count() +1 for t in h.hackathon_team.all()) for h in hackathons),
        "waiting_teams": sum(h.hackathon_team.filter(status=models.HackathonTeamStatusChoices.WAITING).count() for h in hackathons),
    }


    number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
    
    return render(request,'home.html',{
        "line_labels": line_labels,
        "line_data": line_data,
        "pie_labels": labels,
        "pie_data": data,
        "analysis_data":analysis_data,
        "number_of_waiting_requests":number_of_waiting_requests
        
    })


def dashboard_add_hackathon_view(request:HttpRequest,type:str):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    ALLOWED_TYPES = ['professional', 'basic']
    if not type in ALLOWED_TYPES:
            messages.error(request, f"Sorry ! select valid type","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

    price = 0
    if type == 'professional':
        price=2000
    elif type=='basic':
        price=1000
    else:
        price =0

    
    if request.POST:
        form = forms.CreateHackathon(request.POST)
        if form.is_valid():
            if request.POST['number_of_stages'] == '0':
                form.add_error('stages', "please enter at least one stage !")
            elif request.POST['number_of_tracks'] == '0':
                form.add_error('tracks', "please enter at least one track !")
            else:

                data =request.POST

                try:
                    with transaction.atomic():
                        new_hackathon = models.Hackathon.objects.create(
                            title=request.POST['title'],
                            description=request.POST['description'],
                            location=request.POST['location'],
                            start_date=request.POST['startDate'],
                            end_date= request.POST['endDate'],
                            logo= request.FILES['logo'],
                            min_team_size = request.POST['minTeamSize'],
                            max_team_size = request.POST['maxTeamSize'],
                            status = models.HackathonStatusChoices.CLOSED,
                            organization= request.user

                        )
                        new_hackathon.save()
                        conditions = request.POST.getlist("conditions")
                        for cond in conditions:
                            models.HackathonRequirement.objects.create(hackathon=new_hackathon, description=cond)

                        num_stages = int(request.POST.get("number_of_stages", 0))
                        for i in range(num_stages):
                            new_stage = models.HackathonStage.objects.create(
                                hackathon=new_hackathon,
                                title=data[f"stages[{i}][title]"],
                                description=data[f"stages[{i}][description]"],
                                start_date=data[f"stages[{i}][start_date]"],
                                end_date=data[f"stages[{i}][end_date]"],
                            )
                            if i==0:
                                new_hackathon.current_stage = new_stage
                                new_hackathon.save()
                            

                        num_tracks = int(request.POST.get("number_of_tracks", 0))
                        for j in range(num_tracks):
                            models.HackathonTrack.objects.create(
                                hackathon=new_hackathon,
                                name=data[f"tracks[{j}][name]"],
                                description=data[f"tracks[{j}][description]"],
                            )

                        #prize1 
                        first_prize = models.HackathonPrizes.objects.create(
                            title=request.POST['prizetitle_1'],
                            amount=request.POST['prizeamount_1'],
                            hackathon=new_hackathon,
                        )
                        first_prize.save()

                        second_prize = models.HackathonPrizes.objects.create(
                                title=request.POST['prizetitle_2'],
                                amount=request.POST['prizeamount_2'],
                                hackathon=new_hackathon,
                            )
                        second_prize.save()
                        
                        third_prize = models.HackathonPrizes.objects.create(
                                title=request.POST['prizetitle_3'],
                                amount=request.POST['prizeamount_3'],
                                hackathon=new_hackathon,
                            )
                        third_prize.save()
                        

                        #handle payment 
                        basic_auth = base64.b64encode(f"{PAYMENT_API_KEY}:".encode()).decode()
                        url = "https://api.moyasar.com/v1/invoices"

                        headers = {
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Authorization": f"Basic {basic_auth}"
                        }
                        expires_at = (now() + timedelta(days=1)).isoformat()

                        payload = {
                            "amount": price,
                            "currency": "SAR",
                            "description": f"${type} Hackathon - Create",
                            "success_url": f"{os.getenv('PUBLIC_URL')}/dashboard/payment_completed",
                            "back_url":  f"{os.getenv('PUBLIC_URL')}/dashboard/hackathons?error=True",
                            "expired_at":expires_at
                        }
                        response = requests.post(url, json=payload, headers=headers)
                        data = response.json()
                        new_payment = models.Payment.objects.create(
                            hackathon=new_hackathon,
                            cart_id=data["id"],
                            amount= data['amount'],
                            status=models.HackathonPaymentStatusChoices.WAITING)
                        new_payment.save()

                        return redirect(data["url"])
                except Exception as e:
                    print(e)

                                    
      
        
    else: 
        form = forms.CreateHackathon()

        
    number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()

    return render(request, 'add_hackathon.html', {
        'type': type,
        'price': price,
        'form': form, 
        "number_of_waiting_requests":number_of_waiting_requests

    })

 

def dashboard_hackathon_details_view(request:HttpRequest, id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")
    
    try:
        hackathon = models.Hackathon.objects.get(pk=id)
        teams = hackathon.hackathon_team.filter(status=models.HackathonTeamStatusChoices.ACCEPTED)[:3]


        if not hackathon.organization == request.user:
            messages.error(request, "Hackathon not found.", "bg-red-600")
            return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))        

        total_members = models.TeamMember.objects.filter(team__hackathon=hackathon).count()
        total_submissions = models.TeamSubmission.objects.filter(team__hackathon=hackathon).count()
        total_prizes = hackathon.hackathon_prize.aggregate(total=Sum('amount'))['total'] or 0
        prizes = hackathon.hackathon_prize.order_by('id')

        
        duration = (hackathon.end_date - hackathon.start_date).days + 1
        dates = [hackathon.start_date + timedelta(days=i) for i in range((hackathon.end_date - hackathon.start_date).days + 1)]
        
        tracks = models.HackathonTrack.objects.filter(
            hackathon=hackathon
        ).annotate(
            accepted_teams_count=Count(
                'hackathon_team_track',
                filter=Q(hackathon_team_track__status=models.HackathonTeamStatusChoices.ACCEPTED)
            ),
            

        )
        number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()

        return render(request, 'hackathon_details.html', {
            "hackathon":hackathon,
            "total_members":total_members,
            "duration":duration,
            "total_submissions":total_submissions,
            "total_prizes":total_prizes,
            "prizes":prizes,
            "dates":dates,
            "teams":teams,
            "tracks":tracks,
            "number_of_waiting_requests":number_of_waiting_requests

        })
    except models.Hackathon.DoesNotExist:
        messages.error(request, "Hackathon not found", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))      
      

def dashboard_hackathons_view(request:HttpRequest):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")


    if request.GET.get("search"):
        hackathons = models.Hackathon.objects.filter(Q(title__contains=request.GET.get("search") & Q(organization=request.user)))
    else:
        hackathons = models.Hackathon.objects.filter(organization=request.user)

    filter_by = request.GET.get('filter_by')
    if filter_by:
        if filter_by == 'opened':
            hackathons = hackathons.filter(status=models.HackathonStatusChoices.OPENED)
        elif filter_by == 'closed':
            hackathons = hackathons.filter(status=models.HackathonStatusChoices.CLOSED)
        elif filter_by == 'ongoing':
            hackathons = hackathons.filter(status=models.HackathonStatusChoices.ONGOING)
        elif filter_by == 'finished':
            hackathons = hackathons.filter(status=models.HackathonStatusChoices.FINISHED)


    sort_by = request.GET.get('sort_by')
    if sort_by:
        if sort_by == 'newest':
            hackathons = hackathons.order_by('-created_at') 
        elif sort_by == 'oldest':
            hackathons = hackathons.order_by('created_at') 
    hackathons = hackathons.annotate(
            plan=Case(
                When(hackathon_payment__amount=2000, then=Value("Professional")),
                When(hackathon_payment__amount=1000, then=Value("Basic")),
                default=Value("Other"),
                output_field=CharField(),

            ),
            num_teams=Count('hackathon_team', filter=Q(hackathon_team__status=models.HackathonTeamStatusChoices.ACCEPTED)),
            submissions_count=Count("hackathon_team__team_submission", distinct=True)

        )
    
    

    paginator = Paginator(hackathons, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
    return render(request, 'hackathons.html', {
        "hackathons":page_obj,
        "number_of_waiting_requests":number_of_waiting_requests
    })

def dashboard_judges_view(request:HttpRequest,hackathon_id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")
    
    
    try:
        hackathon = models.Hackathon.objects.get(pk=hackathon_id)

        if hackathon:
            number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
            return render(request, 'judges.html',{
                "hackathon":hackathon,
                "number_of_waiting_requests":number_of_waiting_requests
            })


    except models.Hackathon.DoesNotExist:
        messages.error(request, "Hackathon not found.", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER","dashboard:dashboard_hackathons_view"))        


def dashboard_teams_view(request:HttpRequest,hackathon_id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        hackathon = models.Hackathon.objects.get(pk=hackathon_id)
        if not hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER","dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 
        hackathon_teams = hackathon.hackathon_team.filter(status=models.HackathonTeamStatusChoices.ACCEPTED)
    
        if request.GET.get("search"):
            hackathon_teams = hackathon_teams.filter(name__contains=request.GET.get("search"))


        if request.GET.get("track"):
            try:
                track = models.HackathonTrack.objects.get(pk=request.GET.get("track"))
                if track:
                    hackathon_teams = hackathon_teams.filter(track=track)
            except models.HackathonTrack.DoesNotExist:
                messages.error(request, "track not found.", "bg-red-600")
                return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))      


        paginator = Paginator(hackathon_teams, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        tracks = hackathon.hackathon_track.all()
        number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
        return render(request, 'teams.html',{
            "hackathon_teams":page_obj,
            "tracks":tracks,
            "number_of_waiting_requests":number_of_waiting_requests
        })
    except models.Hackathon.DoesNotExist:
        messages.error(request, " hackathon not found !","bg-red-600")
        redirect_url = request.META.get("HTTP_REFERER","dashboard:dashboard_hackathons_view")
        return redirect(f'{redirect_url}')


def dashboard_track_teams_view(request:HttpRequest,hackathon_id:int, track_id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        hackathon = models.Hackathon.objects.get(pk=hackathon_id)
        track = models.HackathonTrack.objects.get(pk=track_id)
        if not hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER","dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 
        hackathon_teams = hackathon.hackathon_team.filter(Q(status=models.HackathonTeamStatusChoices.ACCEPTED) & Q(track=track))
    
        if request.GET.get("search"):
            hackathon_teams = hackathon_teams.filter(name__contains=request.GET.get("search"))


        if request.GET.get("track"):
            try:
                track = models.HackathonTrack.objects.get(pk=request.GET.get("track"))
                if track:
                    hackathon_teams = hackathon_teams.filter(track=track)
            except models.HackathonTrack.DoesNotExist:
                messages.error(request, "track not found.", "bg-red-600")
                return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))      


        paginator = Paginator(hackathon_teams, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        tracks = hackathon.hackathon_track.all()
        number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
        return render(request, 'teams.html',{
            "hackathon_teams":page_obj,
            "tracks":tracks,
            "number_of_waiting_requests":number_of_waiting_requests
        })

    except models.Hackathon.DoesNotExist:
            messages.error(request, " hackathon not found !","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}')        

    except models.HackathonTrack.DoesNotExist:
            messages.error(request, " track not found !","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}')        



def dashboard_team_details_view(request:HttpRequest,team_id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        team = models.Team.objects.get(pk=team_id)
        if not team.hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER","dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

        number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
        
        return render(request, 'team_details.html', {
            "team":team,
            "number_of_waiting_requests":number_of_waiting_requests
        })


    except models.Team.DoesNotExist:
        messages.error(request, "Team not found", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER","dashboard:dashboard_hackathons_view"))      
      


def dashboard_teams_requests_view(request:HttpRequest):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    hackathons = models.Hackathon.objects.filter(organization=request.user)
    teams_requests = models.Team.objects.filter(
    hackathon__organization=request.user
).exclude(status=models.HackathonTeamStatusChoices.ACCEPTED)

  
    search_name = request.GET.get("search")  
    hackathon_id = request.GET.get("hackathon")  

    if search_name:
        teams_requests = teams_requests.filter(
        Q(name__contains=search_name)
    )
        
    if hackathon_id and hackathon_id.isdigit():
        teams_requests = teams_requests.filter(hackathon__id=hackathon_id)



    paginator = Paginator(teams_requests, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
    return render(request, 'teams_requests.html', {
        "teams_requests":page_obj,
        "hackathons":hackathons,
        "number_of_waiting_requests":number_of_waiting_requests
    })


def dashboard_particepents_view(request:HttpRequest):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")
    
    hackathons = models.Hackathon.objects.filter(organization=request.user)

    members = models.TeamMember.objects.filter(team__hackathon__in=hackathons)\
                                       .select_related('team', 'member', 'team__hackathon').annotate(
            total_hackathons=Count('team__hackathon', distinct=True)
        )
    

    search_name = request.GET.get("search")  
    hackathon_id = request.GET.get("hackathon")  

    if search_name:
        members = members.filter(
        Q(member__first_name__contains=search_name) |
        Q(member__last_name__contains=search_name)
    )
    if hackathon_id and hackathon_id.isdigit():
        members = members.filter(team__hackathon__id=hackathon_id)


    paginator = Paginator(members, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
    return render(request, 'particepents.html',{
        "members": page_obj,
        "hackathons": hackathons, 
        "selected_name": search_name or "",
        "selected_hackathon": int(hackathon_id) if hackathon_id and hackathon_id.isdigit() else None,
        "number_of_waiting_requests":number_of_waiting_requests
         })



def dashboard_ai_feature_view(request: HttpRequest, hackathon_id: int):
    try:
        hackathon = models.Hackathon.objects.get(pk=hackathon_id)
        if hackathon.hackathon_payment.amount != 2000:
            messages.error(request, "Sorry! Your hackathon package is not professional!", "bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(redirect_url)
        
        if not hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER","dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

        if not request.user.is_authenticated or request.user.user_profile.account_type != "organization":
            return redirect("accounting:accounting_signin")

        teams_data = []
        for team in hackathon.hackathon_team.all():
            members = [m.member.first_name for m in team.team_members.all()]

            notes = list(team.team_notes.select_related("judge").values("judge__judge_name", "message", "created_at"))


            teams_data.append({
                "team_name": team.name,
                "track": team.track.name if team.track else None,
                "members": members,
                "judge_notes": notes,
            })

        prompt = f"""
        You are an AI assistant for hackathon analytics.
        Given this hackathon data:

        {teams_data}

        Calculate a list of winning probabilities (in percentage) based on idea, market needs, judges' notes, and any performance indicators

       and for best 5 teams ideas:
        1. Generate badges from: Top Rated, Innovative, High Impact, High Potential, Feasible, and a approximate score out of 5 for each team idea.
        2. Provide a list of 3 short AI insights (1-2 sentences) about the hackathon and team's idea and performance

        and put a best team idea in first one, with Top Rated badge

        Additionally, provide AI insights for the hackathon as a whole (1-2 sentences)

        Return JSON like:
        {{
            "insights": [
                {{
                    "content": ["Insight 1 about hackathon", "Insight 2 about hackathon", "Insight 3 about hackathon"]
                }}
            ],
            "winning_probabilities": [
        {{
            "team_name": "Team X",
            "percentage": 60
        }},
        {{
            "team_name": "Team Y",
            "percentage": 90
        }}
    ],
            "teams": [
                {{
                    "team_name": "Team X",
                    "track_name": "AI/ML",
                    "badges": ["Top Rated", "High Impact"],
                    "score": 4,
                    "ai_insights": "The team has a strong technical approach and high innovation potential."
                }}
            ]
        }}
        """

        
        try:
            response = model.generate_content(prompt)
            text = response.candidates[0].content.parts[0].text
            clean_text = re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
            data = json.loads(clean_text)


        except Exception as e:
            print("AI generation error:", e)

        number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
        return render(request, "ai_feature.html",{
                    "ai_data": data,
                    "number_of_waiting_requests":number_of_waiting_requests

        })

    except models.Hackathon.DoesNotExist:
        messages.error(request, "Sorry! Hackathon not found!", "bg-red-600")
        redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
        return redirect(redirect_url)

@csrf_exempt
def payment_completed(request:HttpRequest):
    try:
        cart_id = request.GET.get('invoice_id')

        payment = models.Payment.objects.get(cart_id=cart_id)
        if payment:
            payment.status = models.HackathonPaymentStatusChoices.COMPLETED
            payment.save()

            hackathon = payment.hackathon
            hackathon.status = models.HackathonStatusChoices.OPENED
            hackathon.save()


        number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
        return render(request, "payment_completed.html", {
            "number_of_waiting_requests":number_of_waiting_requests
        })

    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)



def dashboard_delete_hackathon_view(request:HttpRequest, id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        hackathon = models.Hackathon.objects.get(pk=id)
        if hackathon.logo and hasattr(hackathon.logo, 'path') and os.path.exists(hackathon.logo.path):
            os.remove(hackathon.logo.path)
        
        hackathon.delete()
        
        messages.success(request, "Hackathon deleted successfully.", "bg-green-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))
    
    except models.Hackathon.DoesNotExist:
        raise Http404("Hackathon not found")
    except Exception as e:
        print(f"Error deleting hackathon: {e}")
        redirect_url = request.META.get("HTTP_REFERER","dashboard:dashboard_hackathons_view")
        sep = '&' if '?' in redirect_url else '?'
        return redirect(f'{redirect_url}{sep}error=True')

def dashboard_delete_hackathon_requirement_view(request:HttpRequest,id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        requirement = models.HackathonRequirement.objects.get(pk=id)
        if not requirement.hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER","dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

        requirement.delete()


        
         
        messages.success(request, "Requirement deleted successfully.", "bg-green-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))
    except models.Hackathon.DoesNotExist:
        raise Http404("Hackathon not found")
    except Exception as e:
        print(f"Error deleting hackathon: {e}")
        redirect_url = request.META.get("HTTP_REFERER","dashboard:dashboard_hackathons_view")
        sep = '&' if '?' in redirect_url else '?'
        return redirect(f'{redirect_url}{sep}error=True')
    
def dashboard_delete_hackathon_track_view(request:HttpRequest,id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        track = models.HackathonTrack.objects.get(pk=id)
        if not track.hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER","dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

        track.delete()
        
       
        messages.success(request, "Track deleted successfully.", "bg-green-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))
    except models.Hackathon.DoesNotExist:
        raise Http404("Hackathon not found")
    except Exception as e:
        print(f"Error deleting hackathon: {e}")
        redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
        sep = '&' if '?' in redirect_url else '?'
        return redirect(f'{redirect_url}{sep}error=True')
    

def dashboard_update_hackathon_stage(request:HttpRequest,id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        hackathon = models.Hackathon.objects.get(pk=id)
        if not hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

        stage_id = request.POST.get("current_stage")
        if stage_id:
            stage = models.HackathonStage.objects.get(pk=stage_id)
            hackathon.current_stage = stage
            hackathon.save()
            messages.success(request, f"Current stage updated to '{stage.title}'","bg-green-600")

            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}')
    except models.Hackathon.DoesNotExist:
        raise Http404("Hackathon not found")
    except Exception as e:
        print(f"Error deleting hackathon: {e}")
        redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
        sep = '&' if '?' in redirect_url else '?'
        return redirect(f'{redirect_url}{sep}error=True')
    

def dashboard_update_hackathon_status(request:HttpRequest,id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    if request.POST:
        try:
            hackathon = models.Hackathon.objects.get(pk=id)
            if not hackathon.organization == request.user:
                messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
                redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
                return redirect(f'{redirect_url}') 

            status = request.POST["current_stage"]
            if hackathon and status:
                hackathon.status = status
                hackathon.save()
                messages.success(request, f"Current status updated to '{status}'","bg-green-600")

                redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
                return redirect(f'{redirect_url}')
        except models.Hackathon.DoesNotExist:
            raise Http404("Hackathon not found")
        except Exception as e:
            print(f"Error deleting hackathon: {e}")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            sep = '&' if '?' in redirect_url else '?'
            return redirect(f'{redirect_url}{sep}error=True')
    

def dashboard_attendence_hackathon_view(request:HttpRequest, id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        hackathon = models.Hackathon.objects.get(pk=id)
        if not hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 
        
        selected_date = request.GET.get("date")
        if not selected_date:
            messages.error(request, f"Sorry ! please enter a date","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 
        
        if hackathon:
            teams = models.Team.objects.filter(
                Q(hackathon=hackathon) & Q(status=models.HackathonTeamStatusChoices.ACCEPTED)
            )
            
            attendances = models.attendence.objects.filter(
                team__in=teams, 
                date=selected_date
            )
            
            attendance_dict = {}
            for attendance in attendances:
                attendance_dict[attendance.team.id] = attendance.attend_status
            
            teams_with_status = []
            for team in teams:
                team.current_attendance_status = attendance_dict.get(team.id, None)
                teams_with_status.append(team)
            number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
            return render(request, "attendance_page.html", {
            "hackathon": hackathon,
            "date": selected_date,
            "teams": teams,
            "attendances": attendances,
            "number_of_waiting_requests":number_of_waiting_requests
        })
        
    except models.Hackathon.DoesNotExist:
        messages.error(request, "hackathon not found.", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))        
    

        

def dashboard_set_attendance_view(request, team_id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    team = models.Team.objects.get(pk=team_id)
    if not team.hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

    selected_date = request.POST.get("selected_date")

    if request.method == "POST":
        status = request.POST.get("attend_status")
        if status in dict(models.HackathonAttendenceChoices.choices).keys():
            attend = models.attendence.objects.filter(team=team, date=selected_date).first()

            if attend:
                attend.attend_status = status
                attend.save()
            else:
                models.attendence.objects.create(team=team, date=selected_date, attend_status=status)

            messages.success(request, f"Attendance for {team.name} set to {status}", "bg-green-600")
        else:
            messages.error(request, "Invalid status selected.", "bg-red-600")

    return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))


def dashboard_sign_winners_view(request:HttpRequest,id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")
    try:
        if request.method == "POST":
            hackathon = models.Hackathon.objects.get(pk=id)
            if not hackathon.organization == request.user:
                messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
                redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
                return redirect(f'{redirect_url}') 

            selected_team_ids = []
            prize_team_map = {} 

            for key, value in request.POST.items():
                if "_winner" in key:
                    prize_id = key.split("_")[0]
                    team_id = value[0] if isinstance(value, list) else value
                    selected_team_ids.append(team_id)
                    prize_team_map[prize_id] = team_id

            for team_id in selected_team_ids:
                if selected_team_ids.count(team_id) > 1:
                    messages.error(request, "A team cannot win more than one prize.", "bg-red-600")
                    return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))

            for prize_id, team_id in prize_team_map.items():
                prize = models.HackathonPrizes.objects.get(pk=prize_id, hackathon=hackathon)
                team = prize.hackathon.hackathon_team.get(pk=team_id)
                prize.team = team
                prize.save()
            
            hackathon.status = models.HackathonStatusChoices.FINISHED
            hackathon.save()

            messages.success(request, "Hackathon ENDED, Prizes assigned successfully !", "bg-green-600")
            return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))
        
    except models.Hackathon.DoesNotExist:
        messages.error(request, " hackathon not found !","bg-red-600")
        redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
        return redirect(f'{redirect_url}')
        

def dashboard_delete_team_view(request:HttpRequest,id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        team = models.Team.objects.get(pk=id)
        if not team.hackathon.organization == request.user:
                messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
                redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
                return redirect(f'{redirect_url}') 

        team.delete()
        messages.success(request, "Team deleted successfully.", "bg-green-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))

    except models.Team.DoesNotExist:
        messages.error(request, "Team not found.", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))        
    


def dashboard_delete_team_member_view(request:HttpRequest, member_id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        team_member = models.TeamMember.objects.get(pk=member_id)
        if not team_member.team.hackathon.organization == request.user:
                messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
                redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
                return redirect(f'{redirect_url}') 

        team_member.delete()
        messages.success(request, "Member deleted successfully.", "bg-green-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))

    except models.TeamMember.DoesNotExist:
        messages.error(request, "Team member not found.", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))        
    



def dashboard_add_judges_view(request: HttpRequest, hackathon_id: int):
    try:
        hackathon = models.Hackathon.objects.get(pk=hackathon_id)
        if not hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

    except models.Hackathon.DoesNotExist:
        messages.error(request, "Hackathon not found.", "bg-red-600")
        return redirect("dashboard:dashboard_judges_view", hackathon_id=hackathon_id)

    if request.method == "POST":
        form = forms.addJudge(request.POST)
        if form.is_valid():
            models.Judge.objects.create(
                judge_name=form.cleaned_data['judge_name'],
                judge_email=form.cleaned_data['judge_email'],
                judge_phone=form.cleaned_data['judge_phone'],
                hackathon=hackathon
            )
            messages.success(request, "Judge added successfully!", "bg-green-600")
        else:
            messages.error(request, "Invalid form submission.", "bg-red-600")

    return redirect("dashboard:dashboard_judges_view", hackathon_id=hackathon_id)




def dashboard_delete_judge_view(request:HttpRequest, judge_id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        judge = models.Judge.objects.get(pk=judge_id)
        if not judge.hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

        judge.delete()
        messages.success(request, "Judge deleted successfully.", "bg-green-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))

    except models.Judge.DoesNotExist:
        messages.error(request, "Judge not found.", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))        
    

def dashboard_judge_store_notes_view(request: HttpRequest, team_id: int):
    if not request.user.is_authenticated or request.user.user_profile.account_type != 'organization':
        return redirect("accounting:accounting_signin")

    try:
        team = models.Team.objects.get(pk=team_id)
        if not team.hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

    except models.Team.DoesNotExist:
        messages.error(request, "Team not found.", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))

    if request.method == "POST":
        form = forms.store_judge_notes(request.POST)
        if form.is_valid():
            try:
                judge = models.Judge.objects.get(pk=request.POST['selected_judge'])
                models.JudgeNote.objects.create(
                    team=team,
                    judge=judge,
                    message=request.POST['judge_message']
                )
                messages.success(request, "Judge note added successfully.", "bg-green-600")
            except models.Judge.DoesNotExist:
                messages.error(request, "Judge not found.", "bg-red-600")
        else:
            messages.error(request, "Invalid form submission.", "bg-red-600")

        return redirect("dashboard:dashboard_team_details_view", team_id=team.id)

    return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))


def dashboard_edit_hackathon_view(request:HttpRequest, hackathon_id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        hackathon = models.Hackathon.objects.get(pk=hackathon_id)      
        if not hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

        if request.POST:
            form = forms.CreateHackathon(request.POST, request.FILES)
            if form.is_valid():

                data =request.POST
                hackathon.title=data['title']
                hackathon.description=data['description']
                hackathon.location=data['location']
                hackathon.start_date=data['startDate']
                hackathon.min_team_size=data['minTeamSize']
                hackathon.max_team_size=data['maxTeamSize']
                hackathon.end_date=data['endDate']
                if request.FILES.get('logo'):
                    image_path = os.path.join(settings.MEDIA_ROOT, hackathon.logo.name)
                    if os.path.isfile(image_path):
                        os.remove(image_path)
                    hackathon.logo = request.FILES['logo']
                hackathon.save()
                messages.success(request,"Hackathon updated sucessfully !", 'bg-green-600')
                return redirect("dashboard:dashboard_edit_hackathon_view", hackathon_id=hackathon_id)

        
                                                        
                
            
        else: 
            form = forms.CreateHackathon()

            
        number_of_waiting_requests = models.Team.objects.filter(Q(status=models.HackathonTeamStatusChoices.WAITING) & Q(hackathon__organization=request.user)).count()
        return render(request, 'edit_hackathon.html', {
        'hackathon': hackathon,
        "form":form,
        "number_of_waiting_requests":number_of_waiting_requests
    })


    except models.Hackathon.DoesNotExist:
        messages.error(request, "Hackathon not found", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))      
      



def dashboard_start_hackathon_view(request:HttpRequest, hackathon_id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        hackathon = models.Hackathon.objects.get(pk=hackathon_id)
        if not hackathon.organization == request.user:
            messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
            redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
            return redirect(f'{redirect_url}') 

        hackathon.status = models.HackathonStatusChoices.ONGOING
        hackathon.save()
        teams = models.Team.objects.filter(hackathon=hackathon)
        for team in teams:
            member_count = team.team_members.count() 

            if member_count < hackathon.min_team_size:
                team.status = models.HackathonTeamStatusChoices.REJECTED
            elif member_count > hackathon.max_team_size:
                team.status = models.HackathonTeamStatusChoices.REJECTED
            else:
                team.status = models.HackathonTeamStatusChoices.ACCEPTED

            team.save()
            messages.success(request, "Hackathon started and teams status updated!", "bg-green-600")
            return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))


    except models.Hackathon.DoesNotExist:
        messages.error(request, "Hackathon not found", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))      
      


def dashboard_accept_team_view(request:HttpRequest, team_id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        team = models.Team.objects.get(pk=team_id)
        if not team.hackathon.organization == request.user:
                messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
                redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
                return redirect(f'{redirect_url}') 
        
        total_members = models.Team.objects.filter(hackathon=team.hackathon).aggregate(
        total=Count("team_members"))["total"]
        if not team.hackathon.hackathon_payment.amount == 2000 and total_members > 1000:
                messages.error(request, f"Sorry ! your hackathon package is BASIC ! so you cannot add more than 1000 participants to hackathon.","bg-orange-500")
                redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
                return redirect(f'{redirect_url}')
                     

        team.status = models.HackathonTeamStatusChoices.ACCEPTED
        team.save()
        messages.success(request, f"team {team.name} accepted !", "bg-green-600")
        return redirect("dashboard:dashboard_teams_requests_view")   

    except models.Team.DoesNotExist:
        messages.error(request, "Hackathon not found", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_teams_requests_view"))      
             


def dashboard_reject_team_view(request:HttpRequest, team_id:int):
    if not request.user.is_authenticated or not request.user.user_profile.account_type == 'organization':
        return redirect("accounting:accounting_signin")

    try:
        team = models.Team.objects.get(pk=team_id)
        if not team.hackathon.organization == request.user:
                messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
                redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
                return redirect(f'{redirect_url}') 

        team.status = models.HackathonTeamStatusChoices.REJECTED
        team.save()
        messages.success(request, f"team {team.name} rejected !", "bg-orange-600")
        return redirect("dashboard:dashboard_teams_requests_view")   

    except models.Team.DoesNotExist:
        messages.error(request, "Hackathon not found", "bg-red-600")
        return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_teams_requests_view"))      
             

def dashboard_add_track_view(request: HttpRequest, hackathon_id: int):
    if not request.user.is_authenticated or request.user.user_profile.account_type != 'organization':
        return redirect("accounting:accounting_signin")

    if request.method == "POST":
        try:
            hackathon = models.Hackathon.objects.get(pk=hackathon_id)
            if not hackathon.organization == request.user:
                    messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
                    redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
                    return redirect(f'{redirect_url}') 
            
            form = forms.add_track(request.POST)
            
            if form.is_valid():
                new_track = models.HackathonTrack.objects.create(
                    hackathon=hackathon,
                    name=form.cleaned_data['track_name'],
                    description=form.cleaned_data['track_description'],
                )
                messages.success(request, f"New track '{new_track.name}' added!", "bg-green-600")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}", "bg-red-600")

        except models.Hackathon.DoesNotExist:
            messages.error(request, "Hackathon not found.", "bg-red-600")

        redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
        return redirect(redirect_url)

    messages.error(request, "Invalid request method.", "bg-red-600")
    return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))


def dashboard_add_requirement_view(request:HttpRequest, hackathon_id:int):
    if not request.user.is_authenticated or request.user.user_profile.account_type != 'organization':
        return redirect("accounting:accounting_signin")

    if request.method == "POST":
        try:
            hackathon = models.Hackathon.objects.get(pk=hackathon_id)
            if not hackathon.organization == request.user:
                    messages.error(request, f"Sorry ! you cannot access this page","bg-red-600")
                    redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
                    return redirect(f'{redirect_url}') 
            form = forms.add_requirement(request.POST)
            
            if form.is_valid():
                new_requirement = models.HackathonRequirement.objects.create(
                    hackathon=hackathon,
                    description=request.POST['requirement'],
                )
                messages.success(request, f"New Requirement '{new_requirement.description}' added!", "bg-green-600")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}", "bg-red-600")

        except models.Hackathon.DoesNotExist:
            messages.error(request, "Hackathon not found.", "bg-red-600")

        redirect_url = request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view")
        return redirect(redirect_url)

    messages.error(request, "Invalid request method.", "bg-red-600")
    return redirect(request.META.get("HTTP_REFERER", "dashboard:dashboard_hackathons_view"))

