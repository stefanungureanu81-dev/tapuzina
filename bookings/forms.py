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


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'service', 'date', 'start_time', 'end_time', 'number_of_persons',
            'contact_name', 'contact_phone', 'contact_email',
            'location_address', 'building_name', 'floor', 'apartment_number',
            'parking_available', 'parking_floor', 'parking_spot_number', 'parking_notes',
            'massage_break_start', 'massage_break_end', 'break_duration',
            'access_notes', 'special_requests', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'number_of_persons': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numele persoanei de contact'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon contact'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email contact'}),
            'location_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresa completa'}),
            'building_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numele cladirii (optional)'}),
            'floor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Etaj (ex: 3)'}),
            'apartment_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numar apartament/birou'}),
            'parking_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'parking_floor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Etaj parcare'}),
            'parking_spot_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numar loc parcare'}),
            'parking_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Informatii suplimentare parcare'}),
            'massage_break_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'massage_break_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'break_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 120}),
            'access_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Informatii acces (cod, interfon, etc.)'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Cerinte speciale'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alte observatii'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['service'].empty_label = "Selectati un serviciu"
        self.fields['break_duration'].initial = 30
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')
        
        if start_time and end_time and date:
            if start_time >= end_time:
                raise forms.ValidationError("Ora de sfarsit trebuie sa fie dupa ora de inceput!")
        
        return cleaned_data