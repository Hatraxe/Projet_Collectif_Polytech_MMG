from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
def graphiques(request):
    return render(request, 'graphiques.html')

def indicators(request):
    return render(request, 'indicators.html')

def dashboard(request):
    return render(request, 'dashboard.html')

from django.shortcuts import render

# Create your views here.
