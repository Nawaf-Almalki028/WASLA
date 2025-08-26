from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse


def accounting_signin(request:HttpRequest):
    return render(request, 'main/signin.html')

def accounting_signup(request:HttpRequest):
    return render(request, 'main/signup.html')

def accounting_profile(request:HttpRequest):
    return render(request, 'main/profile.html')

def accounting_edit_profile(request:HttpRequest):
    return render(request, 'main/edit_profile.html')
