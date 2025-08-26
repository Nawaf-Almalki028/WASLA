from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Organization)
admin.site.register(models.Hackathon)
admin.site.register(models.HackathonStage)
admin.site.register(models.HackathonPrizes)
admin.site.register(models.HackathonTrack)
admin.site.register(models.HackathonRequirement)
admin.site.register(models.Team)
admin.site.register(models.TeamMember)
admin.site.register(models.TeamSubmission)

admin.site.register(models.Profile)

admin.site.register(models.JoinRequest)
admin.site.register(models.Payment)