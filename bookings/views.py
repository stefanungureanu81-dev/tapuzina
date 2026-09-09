from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta, date
import calendar
import uuid
from .models import Appointment, Service, WorkingHours, Company
from .forms import RegisterForm, AppointmentForm

def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    companies = Company.objects.filter(is_active=True)
    users = User.objects.filter(is_staff=False)
    appointments = Appointment.objects.all().order_by('-date', '-start_time')[:50]
    
    return render(request, 'admin_dashboard.html', {
        'companies': companies,
        'users': users,
        'appointments': appointments,
    })

@user_passes_test(is_admin)
def add_company(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        cui = request.POST.get('cui')
        address = request.POST.get('address')
        contact_person = request.POST.get('contact_person')
        contact_phone = request.POST.get('contact_phone')
        contact_email = request.POST.get('contact_email')
        
        if name:
            Company.objects.create(
                name=name,
                cui=cui,
                address=address,
                contact_person=contact_person,
                contact_phone=contact_phone,
                contact_email=contact_email,
                is_active=True
            )
            messages.success(request, 'Firma "' + name + '" a fost adaugata cu succes!')
        else:
            messages.error(request, 'Numele firmei este obligatoriu!')
        return redirect('admin_companies')
    return redirect('admin_companies')

@user_passes_test(is_admin)
def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        company_id = request.POST.get('company')
        password = request.POST.get('password')
        
        if username and email and password and company_id:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                company = Company.objects.get(id=company_id)
                messages.success(request, 'Utilizatorul "' + username + '" a fost creat pentru ' + company.name + '!')
            except Exception as e:
                messages.error(request, 'Eroare: ' + str(e))
        else:
            messages.error(request, 'Toate campurile obligatorii trebuie completate!')
        return redirect('admin_users')
    return redirect('admin_users')

def send_welcome_email(user):
    """Trimite email de bun venit catre noul utilizator"""
    subject = f'Bun venit la Tapuzina.ro, {user.first_name or user.username}!'
    message = f'''
Buna {user.first_name or user.username}!

Contul tau la Tapuzina.ro a fost creat cu succes.

Datele tale de autentificare:
- Username: {user.username}
- Email: {user.email}

Pentru a te autentifica si a face programari, acceseaza:
{settings.SITE_URL}/login/

Te rugam sa iti schimbi parola dupa primul login.

Ce poti face in contul tau:
- Programeaza un masaj la birou, la sediul Tapuzina sau la domiciliu
- Vezi istoricul programarilor
- Anuleaza sau reprogrameaza programari

Pentru orice intrebare, nu ezita sa ne contactezi la:
programare@tapuzina.ro

Cu stima,
Echipa Tapuzina.ro
{settings.SITE_URL}
'''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print(f"Email de bun venit trimis catre {user.email}")
    except Exception as e:
        print(f"Eroare la trimiterea emailului de bun venit: {e}")

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Trimite email de bun venit
            send_welcome_email(user)
            
            messages.success(request, 'Cont creat cu succes! Verifica-ti emailul pentru detalii.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Date incorecte')
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    appointments = Appointment.objects.filter(client=request.user).order_by('-date', '-start_time')
    upcoming = appointments.filter(date__gte=timezone.now().date(), status__in=['pending', 'confirmed'])
    history = appointments.filter(date__lt=timezone.now().date()) | appointments.filter(status__in=['cancelled', 'completed'])
    
    # Calendar pentru dashboard
    today = timezone.now().date()
    current_date = request.GET.get('month')
    if current_date:
        try:
            year, month = map(int, current_date.split('-'))
            current_date = date(year, month, 1)
        except:
            current_date = today.replace(day=1)
    else:
        current_date = today.replace(day=1)
    
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(current_date.year, current_date.month)
    
    month_start = current_date.replace(day=1)
    next_month = current_date.replace(day=28) + timedelta(days=4)
    month_end = next_month.replace(day=1) - timedelta(days=1)
    
    # Obtine zilele ocupate cu intervale orare
    occupied = Appointment.objects.filter(
        date__range=[month_start, month_end],
        status__in=['pending', 'confirmed']
    ).values('date', 'start_time', 'end_time')
    
    occupied_slots = {}
    occupied_dates = []
    
    for o in occupied:
        date_key = o['date'].isoformat()
        if date_key not in occupied_slots:
            occupied_slots[date_key] = []
            occupied_dates.append(date_key)
        occupied_slots[date_key].append({
            'start': o['start_time'].strftime('%H:%M'),
            'end': o['end_time'].strftime('%H:%M')
        })
    
    occupied_days = [date.fromisoformat(d).day for d in occupied_dates if date.fromisoformat(d).month == current_date.month]
    
    import json
    slots_json = json.dumps(occupied_slots)
    
    return render(request, 'dashboard.html', {
        'appointments': appointments,
        'upcoming': upcoming,
        'history': history,
        'today': today,
        'current_date': current_date,
        'month_days': month_days,
        'occupied_dates': occupied_days,
        'occupied_slots': occupied_slots,
        'slots_json': slots_json,
        'current_month_name': current_date.strftime('%B %Y'),
        'prev_month': (current_date.replace(day=1) - timedelta(days=1)).replace(day=1),
        'next_month': (current_date.replace(day=28) + timedelta(days=4)).replace(day=1),
    })

def send_confirmation_email(appointment):
    site_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8000'
    confirm_url = site_url + '/confirm/' + appointment.confirmation_token + '/'
    
    start_time_str = appointment.start_time.strftime('%H:%M') if hasattr(appointment.start_time, 'strftime') else str(appointment.start_time)
    end_time_str = appointment.end_time.strftime('%H:%M') if hasattr(appointment.end_time, 'strftime') else str(appointment.end_time)
    
    client_subject = 'Confirmare programare Tapuzina.ro - ' + str(appointment.date)
    client_message = "Buna " + appointment.contact_name + "!\n\n"
    client_message += "Programarea ta la Tapuzina.ro a fost inregistrata cu succes.\n\n"
    client_message += "Detalii programare:\n"
    client_message += "- Serviciu: " + appointment.service.get_service_type_display() + " - " + appointment.service.name + "\n"
    client_message += "- Data: " + str(appointment.date) + "\n"
    client_message += "- Ora: " + start_time_str + " - " + end_time_str + "\n"
    client_message += "- Persoane: " + str(appointment.number_of_persons) + "\n"
    client_message += "- Adresa: " + appointment.location_address + "\n\n"
    client_message += "Pentru a confirma programarea, te rugam sa accesezi linkul de mai jos:\n"
    client_message += confirm_url + "\n\n"
    client_message += "Dupa confirmare, vei primi un email de confirmare finala.\n\n"
    client_message += "Cu stima,\nEchipa Tapuzina.ro"
    
    admin_subject = 'Noua programare - ' + appointment.contact_name + ' - ' + str(appointment.date)
    admin_message = "O noua programare a fost inregistrata!\n\n"
    admin_message += "Detalii programare:\n"
    admin_message += "- Client: " + appointment.contact_name + "\n"
    admin_message += "- Telefon: " + appointment.contact_phone + "\n"
    admin_message += "- Email: " + appointment.contact_email + "\n"
    admin_message += "- Serviciu: " + appointment.service.get_service_type_display() + " - " + appointment.service.name + "\n"
    admin_message += "- Data: " + str(appointment.date) + "\n"
    admin_message += "- Ora: " + start_time_str + " - " + end_time_str + "\n"
    admin_message += "- Persoane: " + str(appointment.number_of_persons) + "\n"
    admin_message += "- Adresa: " + appointment.location_address + "\n\n"
    admin_message += "Status: In asteptare confirmare client\n\n"
    admin_message += "Link confirmare: " + confirm_url + "\n\n"
    admin_message += "Pentru a confirma din admin, acceseaza:\n"
    admin_message += site_url + '/admin/bookings/appointment/' + str(appointment.id) + '/change/'
    
    try:
        send_mail(
            client_subject,
            client_message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.contact_email],
            fail_silently=False,
        )
        
        send_mail(
            admin_subject,
            admin_message,
            settings.DEFAULT_FROM_EMAIL,
            ['orar@tapuzina.ro'],
            fail_silently=False,
        )
    except Exception as e:
        print("Eroare trimitere email: " + str(e))

def confirm_appointment(request, token):
    appointment = get_object_or_404(Appointment, confirmation_token=token)
    
    if appointment.confirmed_by_client:
        messages.info(request, 'Aceasta programare a fost deja confirmata!')
        return redirect('dashboard')
    
    appointment.confirmed_by_client = True
    
    if appointment.confirmed_by_admin:
        appointment.status = 'confirmed'
    
    appointment.save()
    
    if appointment.confirmed_by_admin:
        send_final_confirmation_email(appointment)
    
    messages.success(request, 'Programarea a fost confirmata cu succes!')
    return redirect('dashboard')

def send_final_confirmation_email(appointment):
    subject = 'Programare confirmata - Tapuzina.ro - ' + str(appointment.date)
    
    start_time_str = appointment.start_time.strftime('%H:%M') if hasattr(appointment.start_time, 'strftime') else str(appointment.start_time)
    end_time_str = appointment.end_time.strftime('%H:%M') if hasattr(appointment.end_time, 'strftime') else str(appointment.end_time)
    
    message = "Buna " + appointment.contact_name + "!\n\n"
    message += "Programarea ta la Tapuzina.ro a fost confirmata!\n\n"
    message += "Detalii programare:\n"
    message += "- Serviciu: " + appointment.service.get_service_type_display() + " - " + appointment.service.name + "\n"
    message += "- Data: " + str(appointment.date) + "\n"
    message += "- Ora: " + start_time_str + " - " + end_time_str + "\n"
    message += "- Persoane: " + str(appointment.number_of_persons) + "\n"
    message += "- Adresa: " + appointment.location_address + "\n\n"
    message += "Te asteptam!\n\n"
    message += "Cu stima,\nEchipa Tapuzina.ro"
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.contact_email, 'orar@tapuzina.ro'],
            fail_silently=False,
        )
    except Exception as e:
        print("Eroare trimitere email final: " + str(e))

@login_required
def book_appointment(request):
    services = Service.objects.filter(is_active=True)
    companies = Company.objects.filter(is_active=True)
    today = timezone.now().date()
    
    current_date = request.GET.get('month')
    if current_date:
        try:
            year, month = map(int, current_date.split('-'))
            current_date = date(year, month, 1)
        except:
            current_date = today.replace(day=1)
    else:
        current_date = today.replace(day=1)
    
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(current_date.year, current_date.month)
    
    month_start = current_date.replace(day=1)
    next_month = current_date.replace(day=28) + timedelta(days=4)
    month_end = next_month.replace(day=1) - timedelta(days=1)
    
    # Obtine zilele ocupate cu intervale orare
    occupied = Appointment.objects.filter(
        date__range=[month_start, month_end],
        status__in=['pending', 'confirmed']
    ).values('date', 'start_time', 'end_time')

    occupied_slots = {}
    occupied_dates = []

    for o in occupied:
        date_key = o['date'].isoformat()
        if date_key not in occupied_slots:
            occupied_slots[date_key] = []
            occupied_dates.append(date_key)
        occupied_slots[date_key].append({
            'start': o['start_time'].strftime('%H:%M'),
            'end': o['end_time'].strftime('%H:%M')
        })

    import json
    slots_json = json.dumps(occupied_slots)

    occupied_days = [date.fromisoformat(d).day for d in occupied_dates if date.fromisoformat(d).month == current_date.month]
    
    if request.method == 'POST':
        service_id = request.POST.get('service')
        date_str = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        number_of_persons = request.POST.get('number_of_persons', 1)
        
        if not start_time or not end_time:
            messages.error(request, 'Va rugam sa selectati atat ora de inceput cat si ora de sfarsit!')
            return render(request, 'book_appointment.html', {
                'services': services, 
                'companies': companies,
                'today': today, 
                'month_days': month_days, 
                'occupied_dates': occupied_days, 
                'occupied_slots': occupied_slots,
                'current_date': current_date,
                'month_name': current_date.strftime('%B %Y'),
                'prev_month': (current_date.replace(day=1) - timedelta(days=1)).replace(day=1),
                'next_month': (current_date.replace(day=28) + timedelta(days=4)).replace(day=1),
            })
        
        if service_id and date_str and start_time and end_time:
            service = Service.objects.get(id=service_id)
            
            try:
                start_datetime = datetime.strptime(date_str + ' ' + start_time, "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(date_str + ' ' + end_time, "%Y-%m-%d %H:%M")
            except ValueError:
                messages.error(request, 'Formatul orei este invalid! Folositi formatul HH:MM (ex: 14:30)')
                return render(request, 'book_appointment.html', {
                    'services': services, 
                    'companies': companies,
                    'today': today, 
                    'month_days': month_days, 
                    'occupied_dates': occupied_days, 
                    'occupied_slots': occupied_slots,
                    'current_date': current_date,
                    'month_name': current_date.strftime('%B %Y'),
                    'prev_month': (current_date.replace(day=1) - timedelta(days=1)).replace(day=1),
                    'next_month': (current_date.replace(day=28) + timedelta(days=4)).replace(day=1),
                })
            
            if start_datetime >= end_datetime:
                messages.error(request, 'Ora de sfarsit trebuie sa fie dupa ora de inceput!')
                return render(request, 'book_appointment.html', {
                    'services': services, 
                    'companies': companies,
                    'today': today, 
                    'month_days': month_days, 
                    'occupied_dates': occupied_days, 
                    'occupied_slots': occupied_slots,
                    'current_date': current_date,
                    'month_name': current_date.strftime('%B %Y'),
                    'prev_month': (current_date.replace(day=1) - timedelta(days=1)).replace(day=1),
                    'next_month': (current_date.replace(day=28) + timedelta(days=4)).replace(day=1),
                })
            
            day_of_week = start_datetime.weekday()
            try:
                working_hours = WorkingHours.objects.get(day_of_week=day_of_week, is_working_day=True)
                if start_datetime.time() < working_hours.start_time or end_datetime.time() > working_hours.end_time:
                    messages.error(request, 'Programarea trebuie sa fie in programul de lucru!')
                    return render(request, 'book_appointment.html', {
                        'services': services, 
                        'companies': companies,
                        'today': today, 
                        'month_days': month_days, 
                        'occupied_dates': occupied_days, 
                        'occupied_slots': occupied_slots,
                        'current_date': current_date,
                        'month_name': current_date.strftime('%B %Y'),
                        'prev_month': (current_date.replace(day=1) - timedelta(days=1)).replace(day=1),
                        'next_month': (current_date.replace(day=28) + timedelta(days=4)).replace(day=1),
                    })
                
                # Pauza de masa - comentata temporar
                # if working_hours.lunch_break_start and working_hours.lunch_break_end:
                #     if (start_datetime.time() < working_hours.lunch_break_end and 
                #         end_datetime.time() > working_hours.lunch_break_start):
                #         messages.error(request, 'Programarea se suprapune cu pauza de masa!')
                #         return render(request, 'book_appointment.html', {
                #             'services': services, 
                #             'companies': companies,
                #             'today': today, 
                #             'month_days': month_days, 
                #             'occupied_dates': occupied_days, 
                #             'occupied_slots': occupied_slots,
                #             'current_date': current_date,
                #             'month_name': current_date.strftime('%B %Y'),
                #             'prev_month': (current_date.replace(day=1) - timedelta(days=1)).replace(day=1),
                #             'next_month': (current_date.replace(day=28) + timedelta(days=4)).replace(day=1),
                #         })
            except WorkingHours.DoesNotExist:
                messages.error(request, 'Nu lucram in aceasta zi!')
                return render(request, 'book_appointment.html', {
                    'services': services, 
                    'companies': companies,
                    'today': today, 
                    'month_days': month_days, 
                    'occupied_dates': occupied_days, 
                    'occupied_slots': occupied_slots,
                    'current_date': current_date,
                    'month_name': current_date.strftime('%B %Y'),
                    'prev_month': (current_date.replace(day=1) - timedelta(days=1)).replace(day=1),
                    'next_month': (current_date.replace(day=28) + timedelta(days=4)).replace(day=1),
                })
            
            overlapping = Appointment.objects.filter(
                date=date_str,
                status__in=['pending', 'confirmed']
            )
            for app in overlapping:
                if (start_datetime.time() < app.end_time and end_datetime.time() > app.start_time):
                    messages.error(request, 'Intervalul este deja ocupat!')
                    return render(request, 'book_appointment.html', {
                        'services': services, 
                        'companies': companies,
                        'today': today, 
                        'month_days': month_days, 
                        'occupied_dates': occupied_days, 
                        'occupied_slots': occupied_slots,
                        'current_date': current_date,
                        'month_name': current_date.strftime('%B %Y'),
                        'prev_month': (current_date.replace(day=1) - timedelta(days=1)).replace(day=1),
                        'next_month': (current_date.replace(day=28) + timedelta(days=4)).replace(day=1),
                    })
            
            token = str(uuid.uuid4())
            
            appointment = Appointment.objects.create(
                client=request.user,
                service=service,
                date=date_str,
                start_time=start_time,
                end_time=end_time,
                number_of_persons=int(number_of_persons),
                contact_name=request.POST.get('contact_name', ''),
                contact_phone=request.POST.get('contact_phone', ''),
                contact_email=request.POST.get('contact_email', ''),
                location_address=request.POST.get('location_address', ''),
                building_name=request.POST.get('building_name', ''),
                floor=request.POST.get('floor', ''),
                apartment_number=request.POST.get('apartment_number', ''),
                parking_available=request.POST.get('parking_available') == 'on',
                parking_floor=request.POST.get('parking_floor', ''),
                parking_spot_number=request.POST.get('parking_spot_number', ''),
                parking_notes=request.POST.get('parking_notes', ''),
                access_notes=request.POST.get('access_notes', ''),
                special_requests=request.POST.get('special_requests', ''),
                notes=request.POST.get('notes', ''),
                confirmation_token=token,
                status='pending'
            )
            
            send_confirmation_email(appointment)
            
            messages.success(request, 'Programare creata cu succes! Verifica-ti emailul pentru confirmare.')
            return redirect('dashboard')
    
    return render(request, 'book_appointment.html', {
        'services': services,
        'companies': companies,
        'today': today,
        'month_days': month_days,
        'occupied_dates': occupied_days,
        'occupied_slots': occupied_slots,
        'current_date': current_date,
        'month_name': current_date.strftime('%B %Y'),
        'prev_month': (current_date.replace(day=1) - timedelta(days=1)).replace(day=1),
        'next_month': (current_date.replace(day=28) + timedelta(days=4)).replace(day=1),
    })

@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, id=pk, client=request.user)
    if appointment.status in ['pending', 'confirmed']:
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Programare anulata cu succes!')
    else:
        messages.error(request, 'Aceasta programare nu mai poate fi anulata.')
    return redirect('dashboard')

@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(client=request.user).order_by('-date', '-start_time')
    return render(request, 'my_appointments.html', {'appointments': appointments})

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, id=pk, client=request.user)
    return render(request, 'appointment_detail.html', {'appointment': appointment})

@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    working_hours = WorkingHours.objects.all().order_by('day_of_week')
    services = Service.objects.all().order_by('service_type', 'name')
    companies = Company.objects.filter(is_active=True)
    
    return render(request, 'admin_settings.html', {
        'working_hours': working_hours,
        'services': services,
        'companies': companies,
        'day_names': ['Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri', 'Sambata', 'Duminica'],
        'service_types': Service.SERVICE_TYPES,
    })

@login_required
@user_passes_test(is_admin)
def save_working_hours(request):
    if request.method == 'POST':
        WorkingHours.objects.all().delete()
        
        for day in range(7):
            is_working = request.POST.get(f'is_working_{day}') == 'on'
            start_time = request.POST.get(f'start_time_{day}')
            end_time = request.POST.get(f'end_time_{day}')
            lunch_start = request.POST.get(f'lunch_start_{day}')
            lunch_end = request.POST.get(f'lunch_end_{day}')
            
            if is_working and start_time and end_time:
                WorkingHours.objects.create(
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time,
                    is_working_day=True,
                    lunch_break_start=lunch_start if lunch_start else None,
                    lunch_break_end=lunch_end if lunch_end else None
                )
        
        messages.success(request, 'Programul de lucru a fost actualizat cu succes!')
        return redirect('admin_settings')
    return redirect('admin_settings')

@login_required
@user_passes_test(is_admin)
def save_services(request):
    if request.method == 'POST':
        Service.objects.all().delete()
        
        service_names = request.POST.getlist('service_name[]')
        service_types = request.POST.getlist('service_type[]')
        service_durations = request.POST.getlist('service_duration[]')
        service_max_persons = request.POST.getlist('service_max_persons[]')
        service_active = request.POST.getlist('service_active[]')
        
        for i in range(len(service_names)):
            if service_names[i].strip():
                Service.objects.create(
                    name=service_names[i].strip(),
                    service_type=service_types[i] if i < len(service_types) else 'home',
                    duration_minutes=int(service_durations[i]) if i < len(service_durations) else 60,
                    max_persons=int(service_max_persons[i]) if i < len(service_max_persons) else 1,
                    is_active=service_active[i] == 'on' if i < len(service_active) else True
                )
        
        messages.success(request, 'Serviciile au fost actualizate cu succes!')
        return redirect('admin_settings')
    return redirect('admin_settings')

@login_required
@user_passes_test(is_admin)
def admin_companies(request):
    companies = Company.objects.all().order_by('name')
    return render(request, 'admin_companies.html', {'companies': companies})

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    companies = Company.objects.filter(is_active=True)
    users = User.objects.filter(is_staff=False).order_by('username')
    
    for user in users:
        try:
            user.company = user.company
        except:
            user.company = None
    
    return render(request, 'admin_users.html', {
        'companies': companies,
        'users': users,
    })

@login_required
def confirm_my_appointment(request, pk):
    appointment = get_object_or_404(Appointment, id=pk, client=request.user)
    
    if appointment.confirmed_by_client:
        messages.info(request, 'Aceasta programare a fost deja confirmata!')
        return redirect('dashboard')
    
    appointment.confirmed_by_client = True
    
    if appointment.confirmed_by_admin:
        appointment.status = 'confirmed'
    
    appointment.save()
    
    messages.success(request, 'Programarea a fost confirmata cu succes!')
    return redirect('dashboard')

@login_required
@user_passes_test(is_admin)
def edit_company(request, pk):
    company = get_object_or_404(Company, id=pk)
    
    if request.method == 'POST':
        company.name = request.POST.get('name')
        company.cui = request.POST.get('cui')
        company.address = request.POST.get('address')
        company.contact_person = request.POST.get('contact_person')
        company.contact_phone = request.POST.get('contact_phone')
        company.contact_email = request.POST.get('contact_email')
        company.is_active = request.POST.get('is_active') == 'on'
        company.save()
        messages.success(request, f'Firma "{company.name}" a fost actualizata cu succes!')
        return redirect('admin_companies')
    
    return render(request, 'edit_company.html', {'company': company})

@login_required
@user_passes_test(is_admin)
def edit_user(request, pk):
    user = get_object_or_404(User, id=pk)
    companies = Company.objects.filter(is_active=True)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        
        messages.success(request, f'Utilizatorul "{user.username}" a fost actualizat cu succes!')
        return redirect('admin_users')
    
    return render(request, 'edit_user.html', {
        'user': user,
        'companies': companies,
    })

@login_required
@user_passes_test(is_admin)
def reset_password(request, pk):
    user = get_object_or_404(User, id=pk)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if new_password and len(new_password) >= 6:
            user.set_password(new_password)
            user.save()
            
            subject = 'Parola resetata - Tapuzina.ro'
            message = f'''
Buna {user.first_name or user.username}!

Parola ta pentru contul Tapuzina.ro a fost resetata.

Username: {user.username}
Noua parola: {new_password}

Te rugam sa te autentifici si sa iti schimbi parola dupa primul login.

Link autentificare: https://tapuzina.ro/login/

Cu stima,
Echipa Tapuzina.ro
'''
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, f'Parola pentru "{user.username}" a fost resetata si trimisa pe email!')
            except Exception as e:
                messages.error(request, f'Eroare la trimiterea emailului: {str(e)}')
        else:
            messages.error(request, 'Parola trebuie sa aiba cel putin 6 caractere!')
        return redirect('admin_users')
    
    return render(request, 'reset_password.html', {'user': user})