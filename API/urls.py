from django.urls import path
from . import views  # Assurez-vous que vos vues sont correctement importées

urlpatterns = [
    path('', views.home, name='home'),  # Route pour la page d'accueil
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('graphiques/', views.graphiques, name='graphiques'),
    path('indicators/', views.indicators, name='indicators'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('generate-graph/', views.generate_graph_age, name='generate_graph')
]
