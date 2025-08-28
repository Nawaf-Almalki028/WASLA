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

class addJudge(forms.Form):
    judge_name =forms.CharField(max_length=100)
    judge_email =forms.CharField(max_length=100)
    judge_phone =forms.CharField(max_length=100)

class store_judge_notes(forms.Form):
    selected_judge =forms.CharField(max_length=100)
    judge_message =forms.CharField(max_length=500)
