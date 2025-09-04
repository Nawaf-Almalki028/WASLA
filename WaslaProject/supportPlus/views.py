import os
import json
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from .models import Feedback

try:
    import google.generativeai as genai
    genai.configure(api_key=getattr(settings, 'GEMINI_API_KEY', None))
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

def base_support(request: HttpRequest):
    return render(request, 'main/base_support.html')

def term(request: HttpRequest):
    return render(request, 'main/terms.html')

def fq(request: HttpRequest):
    return render(request, 'main/FQ.html')

def contact(request: HttpRequest):
    if request.method == "POST":
        Feedback.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            feedback_type=request.POST.get('feedback_type'),
            message=request.POST.get('message')
        )
        messages.success(request, f'Thank you {request.POST.get("name")}! Your feedback has been received.')
    return render(request, 'main/contact.html')





def chatbot_response(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Method not allowed', 'response': 'Use POST only.'}, status=405)
    
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'anonymous')

        if not message:
            return JsonResponse({'error': 'Message cannot be empty', 'response': 'Please type a message.'}, status=400)
        if len(message) > 1000:
            return JsonResponse({'error': 'Message too long', 'response': 'Keep message under 1000 characters.'}, status=400)

        try:
            response_text = get_ai_response(message)
        except Exception:
            response_text = get_fallback_response(message)
        
        return JsonResponse({'response': response_text, 'session_id': session_id, 'status': 'success'})

    except Exception:
        return JsonResponse({'error': 'Server error', 'response': 'Technical issues. Try later.'}, status=500)


def get_ai_response(message):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"You are Wasla Hackathon Assistant. Answer clearly and concisely:\n\nQ: {message}\nA:"
    resp = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(max_output_tokens=500)
    )
    return resp.text.strip()

FALLBACK_JSON_PATH = os.path.join(settings.BASE_DIR, "fallback_responses.json")
with open(FALLBACK_JSON_PATH, "r", encoding="utf-8") as f:
    FALLBACK_RESPONSES = json.load(f)

def get_fallback_response(message: str) -> str:
    message_lower = message.lower()

    for _, config in FALLBACK_RESPONSES.items():
        if any(keyword.lower() in message_lower for keyword in config["keywords"]):
            return config["response"]

    return FALLBACK_RESPONSES["default"]["response"]