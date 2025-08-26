from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ACCOUNT_CHOICES = [
        ('personal', 'Personal'),
        ('team', 'Team'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    skills = models.TextField(max_length=300, blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_CHOICES, default='personal')

    def __str__(self):
        return f"{self.user.username} Profile"