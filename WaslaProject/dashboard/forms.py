from django import forms

class CreateHackathon(forms.Form):
    title =forms.CharField(max_length=100)
    location =forms.CharField(max_length=100)
    startDate =forms.DateField()
    endDate =forms.DateField()
    description =forms.CharField(max_length=500)
    minTeamSize = forms.IntegerField()
    maxTeamSize = forms.IntegerField()
    logo = forms.ImageField(required=False)