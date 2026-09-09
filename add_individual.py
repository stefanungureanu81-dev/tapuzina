import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from bookings.models import Company

# Verifică dacă există deja
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
else:
    print("ℹ️ Persoana fizica exista deja!")

# Afișează toate companiile
print("\nCompanii existente:")
for c in Company.objects.all():
    print(f"  - {c.name} (ID: {c.id})")