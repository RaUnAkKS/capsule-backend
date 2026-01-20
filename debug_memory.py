import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.models import Memories
from django.conf import settings

print("Checking Cloudinary Settings:")
print(f"CLOUD_NAME: {settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')}")
print(f"API_KEY: {settings.CLOUDINARY_STORAGE.get('API_KEY')}")
# Don't print secret

try:
    m = Memories.objects.exclude(file='').last()
    if m:
        print(f"\nFound memory {m.id}, type: {m.memory_type}")
        print(f"File field: {m.file}")
        print("Attempting to access url...")
        print(f"URL: {m.file.url}")
    else:
        print("\nNo memory with file found.")
except Exception as e:
    print(f"\nCRASHED: {e}")
    import traceback
    traceback.print_exc()
