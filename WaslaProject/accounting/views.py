from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth import authenticate, login, logout


def accounting_signin(request:HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back {user.username}!")
            return redirect("accounting:accounting_profile")
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
            return redirect("accounting:accounting_register")
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            account_type=account_type,
            phone=phone
        )

        messages.success(request, "Account created successfully!")
        return redirect("accounting:accounting_signin")
        
    return render(request, 'main/signup.html')

def accounting_profile(request:HttpRequest):
    return render(request, 'main/profile.html')

def accounting_edit_profile(request:HttpRequest):
    return render(request, 'main/edit_profile.html')
