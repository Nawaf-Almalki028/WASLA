from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpRequest,HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib.auth.decorators import login_required
from dashboard.models import Profile,ProfileSkills,Hackathon,HackathonTrack,Team,TeamMember,HackathonTeamStatusChoices,JoinRequest


def accounting_signin(request:HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            profile, created = Profile.objects.get_or_create(user=user)
            messages.success(request, f"Welcome back {user.username}!")
            return redirect("accounting:accounting_profile",user.username)
        else:
            messages.error(request, "Invalid username or password")
            return redirect("accounting:accounting_signin")

    return render(request, 'main/signin.html')

def accounting_signup(request:HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        repeat_password = request.POST.get("repeatPassword")
        email = request.POST.get("email")
        account_type = request.POST.get("accountType")
        phone = request.POST.get("phone")

        if password != repeat_password:
            messages.error(request, "Passwords do not match")
            return redirect("accounting:accounting_signup")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("accounting:accounting_signup")
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        Profile.objects.create(
            user=user,
            account_type=account_type,
            phone_number=phone
        )

        messages.success(request, "Account created successfully!")
        return redirect("accounting:accounting_signin")
        
    return render(request, 'main/signup.html')

def accounting_profile(request, username):

    user = get_object_or_404(User, username=username)
    profile = getattr(user, 'user_profile', None)
    if not profile:
        messages.error(request, "Profile not found.")
        return redirect('main:home_view')

    return render(request, 'main/profile.html', {'profile': profile, 'user': user})

@login_required
def accounting_account(request: HttpRequest):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        if "first_name" in request.POST:
            user.first_name = request.POST.get("first_name")
            user.save()
        elif "last_name" in request.POST:
            user.last_name = request.POST.get("last_name")
            user.save()
        elif "email" in request.POST:
            user.email = request.POST.get("email")
            user.save()
        elif "phone_number" in request.POST:
            profile.phone_number = request.POST.get("phone_number")
            profile.save()
        elif "country" in request.POST:
            profile.country = request.POST.get("country")
            profile.save()
        elif "city" in request.POST:
            profile.city = request.POST.get("city")
            profile.save()
        elif "nrole" in request.POST:
            profile.role = request.POST.get("nrole")
            profile.save()
        
        return redirect("accounting:accounting_account")

    return render(request, "main/basic_info.html", {"user": user, "profile": profile})



@login_required
def accounting_edit_profile(request:HttpRequest):
    return render(request, 'main/edit_profile.html')

@login_required
def accounting_skills_bio(request: HttpRequest):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect("accounting:accounting_profile")

    if request.method == "POST":
        new_bio = request.POST.get("bio")
        if new_bio is not None:
            profile.bio = new_bio
            profile.save()
            messages.success(request, "Bio updated successfully!")
        new_skill = request.POST.get("addskill")
        if new_skill:
            ProfileSkills.objects.create(profile=profile, name=new_skill)
            messages.success(request, f"Skill '{new_skill}' added!")

        skill_id_to_delete = request.POST.get("skill_id")
        if skill_id_to_delete:
            try:
                skill = ProfileSkills.objects.get(id=skill_id_to_delete, profile=profile)
                skill.delete()
                messages.success(request, f"Skill '{skill.name}' deleted!")
            except ProfileSkills.DoesNotExist:
                messages.error(request, "Skill not found.")

        return redirect("accounting:accounting_skills_bio")

    skills = ProfileSkills.objects.filter(profile=profile)
    
    return render(request, "main/skills_bio.html", {"profile": profile, "skills": skills})

@login_required
def accounting_social_links(request):
    user = request.user
    profile = getattr(user, 'user_profile', None)
    if not profile:
        messages.error(request, "Profile not found.")
        return redirect('accounting:accounting_profile')

    if request.method == "POST":
        field_map = {
            'linkedinUrl': 'linkedin',
            'githubUrl': 'github',
            'portfolioUrl': 'portfolio',
            'behanceUrl': 'behance',
            'discordUsername': 'discord',
        }

        for post_field, model_field in field_map.items():
            if post_field in request.POST:
                setattr(profile, model_field, request.POST[post_field].strip())
                profile.save()
                messages.success(request, f"{model_field.capitalize()} updated successfully!")
                return redirect('accounting:accounting_social_links')

    return render(request, 'main/social_links.html', {'profile': profile})

@login_required
def accounting_security(request:HttpRequest):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
        elif new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
        else:
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")
            return redirect("accounting:accounting_signin")

    return render(request, 'main/security.html')

@login_required
def accounting_hackathons(request:HttpRequest):
    return render(request, 'main/hackathons.html')

@login_required
def accounting_teams(request):
    user = request.user
    leader_teams = Team.objects.filter(leader=user)
    member_teams = Team.objects.filter(team_members__member=user).exclude(leader=user)

    context = {
        'leader_teams': leader_teams,
        'member_teams': member_teams
    }
    return render(request, 'main/my_teams.html', context)

@login_required
def accounting_create_team(request: HttpRequest, hackathon_id):
    hackathon = get_object_or_404(Hackathon, id=hackathon_id)
    tracks = HackathonTrack.objects.filter(hackathon=hackathon)

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        track_id = request.POST.get("track")

        if name and track_id:
            track = get_object_or_404(HackathonTrack, id=track_id, hackathon=hackathon)
            team = Team.objects.create(
                name=name,
                description=description,
                leader=request.user,
                hackathon=hackathon,
                track=track,
                status=HackathonTeamStatusChoices.WAITING,
            )
            TeamMember.objects.create(member=request.user, team=team)
            return redirect("main:hackathon_details_view", hackathon_id=hackathon.id)

    return render(request, "main/create_team.html", {
        "hackathon": hackathon,
        "tracks": tracks,
    })
@login_required
def accounting_team_page(request: HttpRequest, hackathon_id):
    hackathon = get_object_or_404(Hackathon, id=hackathon_id)

    try:
        team = Team.objects.get(hackathon=hackathon, leader=request.user)
    except Team.DoesNotExist:
        team = None

    members = TeamMember.objects.filter(team=team) if team else []
    join_requests = JoinRequest.objects.filter(team=team) if team else []

    if team and request.method == "POST":
        action = request.POST.get("action")
        request_id = request.POST.get("request_id")
        
        join_request = get_object_or_404(JoinRequest, id=request_id, team=team)

        if action == "accept":
            TeamMember.objects.create(member=join_request.member, team=team)
            join_request.delete()
        elif action == "reject":
            join_request.delete()
        return redirect("main:accounting_team_page", hackathon_id=hackathon.id)

    return render(request, "main/team_page.html", {
        "hackathon": hackathon,
        "team": team,
        "members": members,
        "join_requests": join_requests
    })

@login_required
def accounting_team_request(request: HttpRequest, team_id):
    team = get_object_or_404(Team, id=team_id)

    if request.method == "POST":
        message = request.POST.get("message", "").strip()

        existing_request = JoinRequest.objects.filter(
            member=request.user, team=team, sender="MEMBER"
        ).first()
        if existing_request:
            messages.warning(request, "You already have a pending request for this team.")
            return redirect("accounting:accounting_join_request", team_id=team.id)

        JoinRequest.objects.create(
            member=request.user,
            team=team,
            sender="MEMBER"
        )
        messages.success(request, "Your request has been sent.")
        return redirect("main:home_view", team_id=team.id)

    return render(request, "main/join_request.html", {"team": team, "hackathon": team.hackathon})

@login_required
def accounting_logout(request:HttpRequest):
    logout(request)
    return redirect("main:home_view")


