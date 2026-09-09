from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment, Service, Company

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    # Company devine optional
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_active=True),
        required=False,
        label="Firma (optional)",
        empty_label="Persoana fizica"
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2', 'company']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            if field == 'company':
                self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['company'].help_text = "Selectati o firma sau lasati pentru persoana fizica"