import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartclass.settings')
import django

django.setup()

from django.contrib.auth.models import User

username = 'admin'
password = 'admin123'
email = 'admin@example.com'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username=username, email=email, password=password)
    user.profile.role = 'admin'
    user.profile.save()
    print('Demo admin created: admin / admin123')
else:
    print('Demo admin already exists.')
