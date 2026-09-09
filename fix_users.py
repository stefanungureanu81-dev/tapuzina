import os
import django
from django.contrib.auth.hashers import make_password

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User

def fix_users():
    print("🔧 Reparare utilizatori...")
    
    # Listează toți utilizatorii
    users = User.objects.all()
    print(f"📋 Utilizatori găsiți: {users.count()}")
    
    for u in users:
        print(f"  - {u.username} (email: {u.email})")
    
    # Resetează toate parolele
    for u in users:
        u.set_password('parola123')
        u.save()
        print(f"✅ {u.username}: parola resetată la 'parola123'")
    
    # Asigură admin
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'orar@tapuzina.ro',
            'is_superuser': True,
            'is_staff': True
        }
    )
    admin.set_password('admin123')
    admin.save()
    print(f"✅ Admin: admin / admin123")
    
    # Creează și un test user
    test, created = User.objects.get_or_create(
        username='test',
        defaults={
            'email': 'test@tapuzina.ro'
        }
    )
    test.set_password('test123')
    test.save()
    print(f"✅ Test: test / test123")
    
    print("🎉 Toate parolele au fost resetate!")

if __name__ == "__main__":
    fix_users()