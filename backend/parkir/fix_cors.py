# fix_cors.py
import django
import os
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import execute_from_command_line

def apply_fixes():
    """Apply quick fixes for CORS and authentication"""
    
    # Install required packages
    print("Installing required packages...")
    os.system("pip install django-cors-headers djangorestframework")
    
    print("Fixes applied! Please restart your Django server.")

if __name__ == "__main__":
    apply_fixes()