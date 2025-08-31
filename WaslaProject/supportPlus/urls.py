from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.base_support, name="base_support"),
    path('term/',views.term, name='terms'),
    path('fq/',views.fq, name='FQ'),
    # path('feedback/',views.feedback, name='feedback'),
    path('contact/',views.contact, name='contact'),
    # path("chatbot/get-response/", views.chatbot_response, name="chatbot_response"),

]