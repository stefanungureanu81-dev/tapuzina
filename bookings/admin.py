from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Company, Service, Appointment, WorkingHours

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'cui', 'contact_person', 'contact_phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'cui', 'contact_person']
    list_editable = ['is_active']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'duration_minutes', 'max_persons', 'is_active']
    list_filter = ['service_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_info', 'service', 'date', 'start_time', 'status_badge', 'confirmed_by_client', 'confirmed_by_admin']
    list_filter = ['status', 'date', 'service', 'confirmed_by_client', 'confirmed_by_admin']
    search_fields = ['client__username', 'contact_name', 'contact_phone', 'company__name']
    readonly_fields = ['created_at', 'updated_at', 'confirmation_token']
    date_hierarchy = 'date'
    actions = ['confirm_appointments', 'cancel_appointments']
    
    def appointment_info(self, obj):
        company = f" [{obj.company.name}]" if obj.company else ""
        return format_html(
            '<strong>{}</strong>{}<br><small>{}</small>',
            obj.contact_name,
            company,
            obj.client.username
        )
    appointment_info.short_description = 'Client'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'confirmed': 'success',
            'cancelled': 'danger',
            'completed': 'secondary'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def confirm_appointments(self, request, queryset):
        count = queryset.update(status='confirmed', confirmed_by_admin=True)
        self.message_user(request, f"{count} programari confirmate!")
    confirm_appointments.short_description = "Confirma programarile selectate"
    
    def cancel_appointments(self, request, queryset):
        count = queryset.update(status='cancelled')
        self.message_user(request, f"{count} programari anulate!")
    cancel_appointments.short_description = "Anuleaza programarile selectate"

@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ['get_day_display', 'start_time', 'end_time', 'lunch_break_start', 'lunch_break_end', 'is_working_day']
    list_editable = ['start_time', 'end_time', 'is_working_day']
    
    def get_day_display(self, obj):
        return obj.get_day_of_week_display()
    get_day_display.short_description = 'Ziua'