from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=15, required=False)
    account_type = forms.ChoiceField(choices=[('personal', 'Personal'), ('team', 'Team')], initial='personal')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control bg-Muted bg-none br-none focus-none text-white',
            'placeholder': 'username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control bg-Muted bg-none br-none focus-none text-white',
            'placeholder': 'email'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control bg-Muted bg-none br-none focus-none text-white',
            'placeholder': 'password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control bg-Muted bg-none br-none focus-none text-white',
            'placeholder': 'confirm password'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control bg-Muted bg-none br-none focus-none text-white',
            'placeholder': 'phone number'
        })
        self.fields['account_type'].widget.attrs.update({
            'class': 'form-select bg-none br-none text-white'
        })

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'skills', 'github', 'linkedin']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'skills': forms.TextInput(attrs={'class': 'form-control'}),
            'github': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
        }
        
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

        

# class ContactMessageForm(forms.ModelForm):
#     class Meta:
#         model = Contact
#         fields = ['username', 'email', 'message']
        