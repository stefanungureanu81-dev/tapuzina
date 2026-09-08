import os
import shutil

print("=" * 60)
print("DEPLOY FINAL PE MAGHOST")
print("=" * 60)

# 1. Colectează fișierele statice
print("\n1. Colectare fisiere statice...")
os.system("python manage.py collectstatic --noinput")
print("✅ Fisiere statice colectate!")

# 2. Creează passenger_wsgi.py
print("\n2. Creare passenger_wsgi.py...")
with open('passenger_wsgi.py', 'w', encoding='utf-8') as f:
    f.write('''import os
import sys

sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings_production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
''')
print("✅ passenger_wsgi.py creat!")

# 3. Creează .htaccess
print("\n3. Creare .htaccess...")
with open('.htaccess', 'w', encoding='utf-8') as f:
    f.write('''Options +ExecCGI
AddHandler wsgi-script .py
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ passenger_wsgi.py/$1 [QSA,PT,L]

RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]
''')
print("✅ .htaccess creat!")

print("""
" = " * 60
DEPLOY PREGATIT!
" = " * 60

📁 Fisiere de upload pe MagHost:

1. Toate folderele:
   - bookings/
   - myproject/
   - media/
   - static/
   - staticfiles/

2. Fisierele principale:
   - manage.py
   - passenger_wsgi.py
   - .htaccess
   - requirements.txt
   - db.sqlite3 (daca vrei sa pastrezi datele)

3. Conecteaza-te prin FTP la MagHost si incarca totul in public_html/

4. Pe server, ruleaza:
   cd /home/tapuzina/public_html
   python manage.py migrate --settings=myproject.settings_production
   python manage.py createsuperuser --settings=myproject.settings_production

5. Acceseaza: https://tapuzina.ro
""")