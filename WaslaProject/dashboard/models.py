from django.db import models
from django.contrib.auth.models import User




class HackathonStatusChoices(models.TextChoices):
        OPENED = 'OPENED', 'Opened'
        CLOSED = 'CLOSED', 'Closed'
        ONGOING = 'ONGOING', 'Ongoing'
        FINISHED = 'FINISHED', 'Finished'

class Hackathon(models.Model):
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to="hackathons_logos/",default='hackathons_logos/default.svg')
    start_date = models.DateField()
    end_date = models.DateField()
    max_team_size = models.IntegerField()
    min_team_size = models.IntegerField()
    status = models.CharField(choices=HackathonStatusChoices.choices,max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hackathon_organization")
    current_stage = models.ForeignKey('HackathonStage', on_delete=models.SET_NULL, null=True, blank=True, related_name="current_stage")
    def __str__(self):
        return f"{self.title} Hackathon - for {self.organization.first_name}"


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
      team = models.ForeignKey("Team", on_delete=models.SET_NULL, null=True,blank=True, related_name="winner_team")

      def __str__(self):
        return f"{self.title} Prize"


class HackathonTeamStatusChoices(models.TextChoices):
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        WAITING = 'WAITING', 'Waiting'

class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_leader')
    created_at = models.DateTimeField(auto_now_add=True)
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name="hackathon_team")
    track = models.ForeignKey(HackathonTrack, on_delete=models.CASCADE, related_name="hackathon_team_track")
    status = models.CharField(choices=HackathonTeamStatusChoices.choices, max_length=100, default=HackathonTeamStatusChoices.WAITING)
    def __str__(self):
        return f"{self.name} Project - {self.leader.first_name} Leader"
    


class TeamMember(models.Model):
     member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_member")
     team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_members")
     class Meta:
        unique_together = ('member', 'team')
     def __str__(self):
        return f"{self.member.first_name} member - {self.team.name} Team"
     
ACCOUNT_CHOICES = [
('personal', 'Personal'),
('organization', 'Organization'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    phone_number = models.CharField(max_length=15,null=True,blank=True)
    github = models.URLField(null=True,blank=True)
    portfolio = models.URLField(null=True,blank=True)
    behance = models.URLField(null=True,blank=True)
    discord = models.CharField(max_length=100,null=True,blank=True)
    skills = models.TextField(max_length=300,null=True, blank=True)
    bio = models.TextField(max_length=500,null=True, blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    linkedin = models.URLField(null=True,blank=True)
    role = models.CharField(max_length=100,null=True,blank=True)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_CHOICES, default='personal')
    
    def __str__(self):
        return f"{self.user.first_name}'s Profile"

class ProfileSkills(models.Model):
     name = models.CharField(max_length=100)
     profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile_skills")
     def __str__(self):
        return f"{self.profile.user.first_name}'s Skills"

class HackathonJoinRequestSenderChoices(models.TextChoices):
        TEAM = 'TEAM', 'Team'
        MEMBER = 'MEMBER', 'Member'
 
class JoinRequest(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="member_request")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_request")
    sender = models.CharField(choices=HackathonJoinRequestSenderChoices.choices,max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.member.first_name}'s request - {self.team.name} team"


class TeamSubmission(models.Model):
     name = models.CharField(max_length=100)
     file = models.FileField(upload_to='uploads/')
     team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_submission")
     created_at = models.DateTimeField(auto_now_add=True)
     def __str__(self):
        return f"{self.team.name} Team - Submission"




class HackathonPaymentStatusChoices(models.TextChoices):
        WAITING = 'WAITING', 'Waiting'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELED = 'CANCELED', 'Canceled'

class Payment(models.Model):
    hackathon = models.OneToOneField(Hackathon,on_delete=models.CASCADE, related_name="hackathon_payment")
    cart_id=models.TextField()
    amount = models.IntegerField()
    status = models.CharField(choices=HackathonPaymentStatusChoices.choices,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.hackathon.title}'s Hackathon Payment"


class HackathonAttendenceChoices(models.TextChoices):
        ATTEND = 'ATTEND', 'Attend'
        ABSENT = 'ABSENT', 'Absent'

class attendence(models.Model):
    team= models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_attend")
    date = models.DateField()
    attend_status = models.CharField(choices=HackathonAttendenceChoices.choices,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
                return f"{self.team.name}'s Team attendence - for {self.date}"


class Judge(models.Model):
        hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name="hackathon_judges")
        judge_name = models.CharField(max_length=100)
        judge_email = models.EmailField(max_length=100)
        judge_phone = models.CharField(max_length=100)  
        def __str__(self):
                return f"{self.judge_name} judge"


class JudgeNote(models.Model):
        team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_notes")
        judge = models.ForeignKey(Judge, on_delete=models.CASCADE, related_name="judges_notes")
        message = models.TextField()
        created_at = models.DateTimeField(auto_now_add=True)
        def __str__(self):
                return f"{self.team.name} Notes - by {self.judge.judge_name}"


