from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse


def main_test(request:HttpRequest):
    return render(request, 'main/test.html')