import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from bookings.models import Company, Service, WorkingHours
from django.contrib.auth.models import User

# 1. Adaugă Persoana fizică
if not Company.objects.filter(name="Persoana fizica").exists():
    Company.objects.create(
        name="Persoana fizica",
        cui="",
        address="",
        contact_person="",
        contact_phone="",
        contact_email="",
        is_active=True
    )
    print("✅ Persoana fizica adaugata!")

# 2. Adaugă servicii default (dacă nu există)
if Service.objects.count() == 0:
    services = [
        {'name': 'Masaj la birou', 'service_type': 'office', 'duration_minutes': 60, 'max_persons': 10},
        {'name': 'Masaj la sediu', 'service_type': 'studio', 'duration_minutes': 60, 'max_persons': 10},
        {'name': 'Masaj la domiciliu', 'service_type': 'home', 'duration_minutes': 60, 'max_persons': 10},
    ]
    for s in services:
        Service.objects.create(**s, is_active=True)
    print("✅ Servicii adaugate!")

# 3. Adaugă program de lucru (dacă nu există)
if WorkingHours.objects.count() == 0:
    days = [
        {'day': 0, 'start': '09:00', 'end': '21:00', 'lunch_start': '13:00', 'lunch_end': '14:00'},
        {'day': 1, 'start': '09:00', 'end': '21:00', 'lunch_start': '13:00', 'lunch_end': '14:00'},
        {'day': 2, 'start': '09:00', 'end': '21:00', 'lunch_start': '13:00', 'lunch_end': '14:00'},
        {'day': 3, 'start': '09:00', 'end': '21:00', 'lunch_start': '13:00', 'lunch_end': '14:00'},
        {'day': 4, 'start': '09:00', 'end': '21:00', 'lunch_start': '13:00', 'lunch_end': '14:00'},
        {'day': 5, 'start': '10:00', 'end': '18:00', 'lunch_start': '14:00', 'lunch_end': '15:00'},
    ]
    for d in days:
        WorkingHours.objects.create(
            day_of_week=d['day'],
            start_time=d['start'],
            end_time=d['end'],
            is_working_day=True,
            lunch_break_start=d['lunch_start'],
            lunch_break_end=d['lunch_end']
        )
    print("✅ Program de lucru adaugat!")

print("✅ Bootstrap complet!")