import cloudinary
from django.conf import settings
from decouple import config

CLOUDINARY = settings.CLOUDINARY_STORAGE

CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME")
API_KEY = config("CLOUDINARY_API_KEY")
API_SECRET = config("CLOUDINARY_API_SECRET")

def cloudinary_init():
    cloudinary.config( 
    cloud_name = CLOUDINARY.CLOUD_NAME, 
    api_key = CLOUDINARY.API_KEY,
    api_secret = CLOUDINARY.API_SECRET
    )

