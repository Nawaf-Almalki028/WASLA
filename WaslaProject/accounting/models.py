from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ACCOUNT_CHOICES = (
        ('personal', 'Personal Account'),
        ('company', 'Company Account'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_CHOICES, default='personal')
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_type}"