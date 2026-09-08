
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Company(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nume firma")
    cui = models.CharField(max_length=50, blank=True, verbose_name="CUI")
    address = models.TextField(blank=True, verbose_name="Adresa firma")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Persoana contact")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon contact")
    contact_email = models.EmailField(blank=True, verbose_name="Email contact")
    is_active = models.BooleanField(default=True, verbose_name="Activ")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firme"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Service(models.Model):
    SERVICE_TYPES = [
        ('office', 'La Birou'),
        ('studio', 'La Sediu Tapuzina'),
        ('home', 'La Domiciliu'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nume serviciu")
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name="Tip serviciu")
    duration_minutes = models.IntegerField(default=60, verbose_name="Durata standard (minute)")
    max_persons = models.IntegerField(default=10, verbose_name="Numar maxim persoane")
    is_active = models.BooleanField(default=True, verbose_name="Activ")
    description = models.TextField(blank=True, verbose_name="Descriere")
    image = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name="Imagine")
    
    class Meta:
        verbose_name = "Serviciu"
        verbose_name_plural = "Servicii"
        ordering = ['service_type', 'name']
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.name}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'In asteptare'),
        ('confirmed', 'Confirmata'),
        ('cancelled', 'Anulata'),
        ('completed', 'Finalizata'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='appointments', verbose_name="Firma")
    
    contact_name = models.CharField(max_length=100, verbose_name="Nume contact")
    contact_phone = models.CharField(max_length=20, verbose_name="Telefon contact")
    contact_email = models.EmailField(verbose_name="Email contact")
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Serviciu")
    date = models.DateField(verbose_name="Data")
    start_time = models.TimeField(verbose_name="Ora inceput")
    end_time = models.TimeField(verbose_name="Ora sfarsit")
    number_of_persons = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)], verbose_name="Numar persoane")
    
    massage_break_start = models.TimeField(blank=True, null=True, verbose_name="Pauza masor - inceput")
    massage_break_end = models.TimeField(blank=True, null=True, verbose_name="Pauza masor - sfarsit")
    break_duration = models.IntegerField(default=30, verbose_name="Durata pauza (minute)")
    
    location_address = models.TextField(verbose_name="Adresa completa")
    building_name = models.CharField(max_length=200, blank=True, verbose_name="Nume cladire")
    floor = models.CharField(max_length=20, blank=True, verbose_name="Etaj")
    apartment_number = models.CharField(max_length=20, blank=True, verbose_name="Numar apartament/birou")
    
    parking_available = models.BooleanField(default=False, verbose_name="Parcare disponibila")
    parking_floor = models.CharField(max_length=20, blank=True, verbose_name="Etaj parcare")
    parking_spot_number = models.CharField(max_length=20, blank=True, verbose_name="Numar loc parcare")
    parking_notes = models.TextField(blank=True, verbose_name="Informatii parcare")
    
    access_notes = models.TextField(blank=True, verbose_name="Informatii acces")
    special_requests = models.TextField(blank=True, verbose_name="Cerinte speciale")
    notes = models.TextField(blank=True, verbose_name="Alte observatii")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    confirmation_token = models.CharField(max_length=100, blank=True, null=True, verbose_name="Token confirmare")
    confirmed_by_client = models.BooleanField(default=False, verbose_name="Confirmat de client")
    confirmed_by_admin = models.BooleanField(default=False, verbose_name="Confirmat de admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Programare"
        verbose_name_plural = "Programari"
        ordering = ['-date', '-start_time']
    
    def __str__(self):
        company_name = f" ({self.company.name})" if self.company else ""
        return f"{self.client.username}{company_name} - {self.service.name} - {self.date}"

class WorkingHours(models.Model):
    DAY_CHOICES = [
        (0, 'Luni'),
        (1, 'Marti'),
        (2, 'Miercuri'),
        (3, 'Joi'),
        (4, 'Vineri'),
        (5, 'Sambata'),
        (6, 'Duminica'),
    ]
    
    day_of_week = models.IntegerField(choices=DAY_CHOICES, verbose_name="Ziua")
    start_time = models.TimeField(verbose_name="Ora deschidere")
    end_time = models.TimeField(verbose_name="Ora inchidere")
    is_working_day = models.BooleanField(default=True, verbose_name="Zi lucratoare")
    lunch_break_start = models.TimeField(blank=True, null=True, verbose_name="Pauza masa - inceput")
    lunch_break_end = models.TimeField(blank=True, null=True, verbose_name="Pauza masa - sfarsit")
    
    class Meta:
        verbose_name = "Program de lucru"
        verbose_name_plural = "Program de lucru"
        ordering = ['day_of_week']
    
    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.start_time} - {self.end_time}"
