import cloudinary
import cloudinary.uploader
import os

# Configurare Cloudinary - înlocuiește cu datele tale
cloudinary.config(
    cloud_name='tpolhmze',
    api_key='478478266754522',
    api_secret='qGEjONLlGBRPHVsdPH6fosyKZPE'
)

# Încarcă imagini
images = [
    'media/services/fundal.png',
    'media/services/masaj1.png',
    'media/services/masaj2.png',
    'media/services/masaj3.png',
    'media/services/scaun.png',
]

for image in images:
    if os.path.exists(image):
        result = cloudinary.uploader.upload(image, folder='tapuzina/services')
        print(f"Uploaded {image}: {result['secure_url']}")

# Încarcă video
video = 'media/video/promo.mp4'
if os.path.exists(video):
    result = cloudinary.uploader.upload(video, resource_type='video', folder='tapuzina/video')
    print(f"Uploaded video: {result['secure_url']}")

print("Done!")