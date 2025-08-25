from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse


def dashboard_test(request:HttpRequest):
    return render(request, 'main/dashboard.html')