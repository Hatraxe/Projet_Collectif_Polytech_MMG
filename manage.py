import os
import sys
import webbrowser
from threading import Timer
import subprocess
def open_browser():
    webbrowser.open_new('http://127.0.0.1:8080/')

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
    from django.core.management import execute_from_command_line

    # Démarrer le serveur Django sans rechargement automatique
    Timer(1.5, open_browser).start()
    execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8080', '--noreload'])
    # Fermer la console après le lancement
    subprocess.Popen('TASKKILL /F /PID {pid} /T'.format(pid=os.getpid()), shell=True)
if __name__ == "__main__":
    main()