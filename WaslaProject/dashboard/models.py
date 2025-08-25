from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="logos/",default='logos/default.jpg')
    manager = models.OneToOneField(User, on_delete=models.CASCADE, related_name="organization_manager")
    def __str__(self):
        return f"{self.name} Organization"


class HackathonStatusChoices(models.TextChoices):
        OPENED = 'OPENED', 'Opened'
        CLOSED = 'CLOSED', 'Closed'
        ONGOING = 'ONGOING', 'Ongoing'
        FINISHED = 'FINISHED', 'Finished'

class Hackathon(models.Model):
    title = models.CharField(max_length=100)
    location = models.URLField()
    logo = models.ImageField(upload_to="hackathons_logos/",default='hackathons_logos/default.jpg')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(auto_now_add=True)
    max_team_size = models.IntegerField()
    min_team_size = models.IntegerField()
    status = models.CharField(choices=HackathonStatusChoices.choices,max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="hackathon_organization")
    def __str__(self):
        return f"{self.title} Hackathon - for {self.organization.name} organization"


class HackathonStage(models.Model):
      title = models.CharField(max_length=100)
      description = models.TextField()
      start_date = models.DateField(auto_now_add=True)
      end_date = models.DateField(auto_now_add=True)
      hackathon = models.ForeignKey(Hackathon,on_delete=models.CASCADE, related_name="hackathon_stage")
      def __str__(self):
        return f"{self.title} Stage"


class HackathonTrack(models.Model):
      name = models.CharField(max_length=100)
      description = models.TextField()
      hackathon = models.ForeignKey(Hackathon,on_delete=models.CASCADE, related_name="hackathon_track")

      def __str__(self):
        return f"{self.name} Track"

class HackathonRequirement(models.Model):
      description = models.TextField()
      hackathon = models.ForeignKey(Hackathon,on_delete=models.CASCADE, related_name="hackathon_requirement")

      def __str__(self):
        return f"{self.description} Requirement"

class HackathonPrizes(models.Model):
      title = models.CharField(max_length=100)
      amount = models.CharField(max_length=200)
      hackathon = models.ForeignKey(Hackathon,on_delete=models.CASCADE, related_name="hackathon_prize")

      def __str__(self):
        return f"{self.title} Prize"

    
class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_leader')
    members = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team')
    created_at = models.DateTimeField(auto_now_add=True)
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name="hackathon")
    track = models.ForeignKey(HackathonTrack, on_delete=models.CASCADE, related_name="hackahton_track")
    
    
    def __str__(self):
        return f"{self.name} Project - {self.leader.first_name} Leader"
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15)
    github = models.URLField()
    linedin = models.URLField()
    skills = models.TextField()
    role = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    team = models.ManyToManyField(Team, related_name="user_teams", null=True,blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="organization_admin",null=True,blank=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"



class RequestJoinChoices(models.TextChoices):
        pending = 'PENDING', 'Pending'
        accepted = 'ACCEPTED', 'Accepted'
        rejected = 'REJECTED', 'Rejected'

class JoinRequest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_request')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_request")
    status = models.CharField(choices=RequestJoinChoices.choices,max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s request - {self.team.name} team"

class TeamSubmission(models.Model):
     title = models.CharField(max_length=100)
     file = models.URLField()
     team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_submission")
     created_at = models.DateTimeField(auto_now_add=True)
     def __str__(self):
        return f"{self.title}'s Request - {self.team.name} Team"




class HackathonPaymentStatusChoices(models.TextChoices):
        WAITING = 'WAITING', 'Waiting'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELED = 'CANCELED', 'Canceled'

class Payment(models.Model):
    hackathon = models.ForeignKey(Hackathon,on_delete=models.CASCADE, related_name="hackathon_payment")
    cart_id=models.TextField()
    amount = models.IntegerField()
    status = models.CharField(choices=HackathonPaymentStatusChoices.choices,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.hackathon.title}'s Hackathon Payment"


