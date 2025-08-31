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
        return redirect('support:contact')
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
    return resp.text.strip() if resp.text else get_fallback_response(message)


def get_fallback_response(message):
    message_lower = message.lower()

    if any(word in message_lower for word in ['who designed you', 'who created you', 'من صممتك', 'من هو مصممك']):
        return "💻 صمّمني فريق موقع وصلة."

    if any(word in message_lower for word in ['register', 'sign up', 'join', 'participate', 'how to join']):
        return "📝 To join Wasla Hackathon: visit Waslehaktons.com → Click 'Register Now'. For help, contact support@waslahackathon.com"
    
    elif any(word in message_lower for word in ['prize', 'award', 'reward', 'win']):
        return "🏆 Wasla Hackathon prizes info: visit Waslehaktons.com or contact info@waslahackathon.com"

    elif any(word in message_lower for word in ['schedule', 'timeline', 'date', 'time']):
        return "📅 Check the event schedule at Waslehaktons.com or contact info@waslahackathon.com"

    elif any(word in message_lower for word in ['team', 'group', 'partner', 'collaborate']):
        return "🤝 Teams: register individually or as a team (3-5 members). Join team formation sessions via our Discord/Slack channels."

    elif any(word in message_lower for word in ['contact', 'support', 'help', 'email', 'phone', 'reach']):
        return "📞 Contact support: support@waslahackathon.com | +017345872"

    else:
        return "👋 Hello! I can help with Registration, Prizes, Schedule, Teams, Technical info, or Contact. For other questions, try contacting support@waslahackathon.com"
