from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Feedback

def base_support(request: HttpRequest):
    return render(request, 'main/base_support.html')

def term(request: HttpRequest):
    return render(request, 'main/terms.html')

def fq(request: HttpRequest):
    return render(request, 'main/FQ.html')

def contact(request: HttpRequest):
    if request.method == "POST":
        feedback_obj = Feedback.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            feedback_type=request.POST.get('feedback_type'),
            message=request.POST.get('message')
        )
        messages.success(request, f'Thank you {feedback_obj.name}! Your feedback has been received successfully.')
        return redirect('support:contact')  
    return render(request, 'main/contact.html')