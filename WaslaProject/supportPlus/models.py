from django.db import models

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('general', 'General'),
        ('suggestion', 'Improvement Suggestion'),
        ('complaint', 'Complaint'),
        ('praise', 'Praise'),
        ('bug_report', 'Bug Report'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='general')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.feedback_type})"
