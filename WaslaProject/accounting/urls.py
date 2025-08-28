from django.urls import path,include
from . import views



app_name = 'accounts'

urlpatterns = [
    
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('term/',views.term, name='terms'),
    path('FQ',views.FQ_view, name='FQ'),
    path('feedback/',views.feedback, name='feedback'),
    path('contact',views.contact, name='contact')
]