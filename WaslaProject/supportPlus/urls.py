from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.base_support, name="base_support"),
    path('term/',views.term, name='terms'),
    path('FQ',views.fq, name='FQ'),
    # path('feedback/',views.feedback, name='feedback'),
    path('contact',views.contact, name='contact'),
]