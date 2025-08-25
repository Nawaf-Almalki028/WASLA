from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse


def accounting_test(request:HttpRequest):
    return render(request, 'main/accounting.html')