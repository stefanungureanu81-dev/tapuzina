import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 50)
print("UTILIZATORI EXISTENTI IN BAZA DE DATE")
print("=" * 50)

users = User.objects.all()

if users.count() == 0:
    print("❌ Nu exista utilizatori in baza de date!")
else:
    print(f"✅ Total utilizatori: {users.count()}")
    print("-" * 50)
    for user in users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Admin: {'✅' if user.is_superuser else '❌'}")
        print(f"Activ: {'✅' if user.is_active else '❌'}")
        print(f"Data creare: {user.date_joined}")
        print("-" * 50)