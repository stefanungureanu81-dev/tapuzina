import os
import shutil

print("=" * 50)
print("PREGATIRE DEPLOY PE MAGHOST")
print("=" * 50)

# 1. Instalează dependințele
print("\n1. Instalează dependințele pentru producție...")
os.system("pip install whitenoise gunicorn")
os.system("pip freeze > requirements.txt")
print("✅ Dependințe instalate!")

# 2. Creează folderul staticfiles
print("\n2. Colectează fișierele statice...")
os.makedirs('staticfiles', exist_ok=True)
os.system("python manage.py collectstatic --noinput")
print("✅ Fișiere statice colectate!")

# 3. Creează passenger_wsgi.py
print("\n3. Creează passenger_wsgi.py...")
with open('passenger_wsgi.py', 'w', encoding='utf-8') as f:
    f.write('''import os
import sys

sys.path.append(os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
''')
print("✅ passenger_wsgi.py creat!")

# 4. Creează .htaccess
print("\n4. Creează .htaccess...")
with open('.htaccess', 'w', encoding='utf-8') as f:
    f.write('''# .htaccess pentru MagHost
Options +ExecCGI
AddHandler wsgi-script .py
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ passenger_wsgi.py/$1 [QSA,PT,L]
''')
print("✅ .htaccess creat!")

print("\n" + "=" * 50)
print("DEPLOY PREGATIT!")
print("=" * 50)
print("""
Următorii pași pentru upload pe MagHost:

1. Conectează-te la MagHost prin FTP
2. Încarcă toate fișierele din acest folder în directorul public
3. Asigură-te că folderul media/ are permisiuni de scriere
4. Accesează: https://tapuzina.ro

📁 Fisiere importante:
- passenger_wsgi.py
- .htaccess
- manage.py
- bookings/
- myproject/
- media/
- static/
- staticfiles/
- requirements.txt
- db.sqlite3 (dacă folosești SQLite)

🔑 Admin: https://tapuzina.ro/admin
📧 Email: orar@tapuzina.ro
""")