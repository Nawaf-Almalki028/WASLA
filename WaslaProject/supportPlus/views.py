from django.http import HttpRequest,HttpResponse
from django.shortcuts import render

# Create your views here.
def base_support(request:HttpRequest):
    return render(request, 'main/base_support.html' )