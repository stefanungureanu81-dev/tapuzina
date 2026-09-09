import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 50)
print("UTILIZATORI EXISTENTI")
print("=" * 50)

users = User.objects.all()

if users:
    for user in users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Admin: {user.is_superuser}")
        print(f"Activ: {user.is_active}")
        print("-" * 30)
    print(f"Total: {users.count()} utilizatori")
else:
    print("Nu exista utilizatori!")