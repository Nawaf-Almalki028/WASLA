from django.contrib import admin
from django.urls import path,include
from . import views

app_name = "accounting"

urlpatterns = [
    path('signin/', views.accounting_signin, name='accounting_signin'),
    path('signup/', views.accounting_signup, name='accounting_signup'),
    path('profile/', views.accounting_profile, name='accounting_profile'),
    path('edit_profile/', views.accounting_edit_profile, name='accounting_edit_profile'),
    path('logout/', views.accounting_logout, name='accounting_logout'),
    path('term/',views.term, name='terms'),
    path('FQ',views.FQ_view, name='FQ'),
    path('feedback/',views.feedback, name='feedback'),
    path('contact',views.contact, name='contact'),
]

