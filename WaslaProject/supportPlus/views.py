from django.http import HttpRequest,HttpResponse
from django.shortcuts import render

# Create your views here.
def base_support(request:HttpRequest):
    return render(request, 'main/base_support.html' )




def term(request):

 return render(request, 'main/terms.html')


def feedback(request):

 return render(request,'main/feedback.html')


def contact(request):

    return render(request,'main/contact.html')

def FQ_view(request):
    return render(request,'main/FQ.html')