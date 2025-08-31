from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import google.generativeai as genai
from django.conf import settings
from django.contrib import messages
from .models import Feedback

# genai.configure(api_key=settings.GEMINI_API_KEY)

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

# def chatbot_response(request: HttpRequest):
#     user_message = request.GET.get("message", "").strip()

#     if not user_message:
#         return JsonResponse({"reply": "⚠️ Please type a message first."})

#     try:
#         model = genai.GenerativeModel("gemini-pro")
#         response = model.generate_content(user_message)
#         bot_reply = response.text if response else "⚠️ Error from Gemini API"
#     except Exception as e:
#         bot_reply = f"⚠️ Error: {str(e)}"

#     return JsonResponse({"reply": bot_reply})
