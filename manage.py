import os
import sys
import webbrowser
from threading import Timer

def open_browser():
      webbrowser.open_new('http://127.0.0.1:8080/')

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
    from django.core.management import execute_from_command_line

    # Démarrer le serveur Django
    Timer(1.5, open_browser).start()
    execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8080'])
    execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8080'])
    # Ajustez cette ligne dans votre script Python
    execute_from_command_line(['manage.py', 'runserver', '8080'])


if __name__ == "__main__":
    main()

