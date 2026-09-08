import os

print("=" * 50)
print("CREARE FOLDERE LIPSA")
print("=" * 50)

folders = [
    'static',
    'static/images',
    'static/css',
    'static/js',
    'staticfiles',
    'media',
    'media/services',
    'media/video',
]

for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"✅ Creat: {folder}")
    else:
        print(f"ℹ️ Exista deja: {folder}")

print("\n" + "=" * 50)
print("FOLDERE CREATE!")
print("""
Acum copiază pozele:

copy media\services\*.png static\images\

Apoi ruleaza:
python manage.py collectstatic --noinput
""")