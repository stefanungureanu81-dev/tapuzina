from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('appointment/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('cancel/<int:pk>/', views.cancel_appointment, name='cancel_appointment'),
    
    # Admin URLs
    path('admin-settings/', views.admin_settings, name='admin_settings'),
    path('admin-companies/', views.admin_companies, name='admin_companies'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('save-working-hours/', views.save_working_hours, name='save_working_hours'),
    path('save-services/', views.save_services, name='save_services'),
    path('add-company/', views.add_company, name='add_company'),
    path('add-user/', views.add_user, name='add_user'),
    path('confirm/<str:token>/', views.confirm_appointment, name='confirm_appointment'),
    path('confirm-my/<int:pk>/', views.confirm_my_appointment, name='confirm_my_appointment'),
    path('edit-company/<int:pk>/', views.edit_company, name='edit_company'),
    path('edit-user/<int:pk>/', views.edit_user, name='edit_user'),
    path('view-users/', views.view_users, name='view_users'),
path('reset-password/<int:pk>/', views.reset_password, name='reset_password'),
]