from django.urls import path
from API import views  # Assurez-vous que vos vues sont correctement importées

urlpatterns = [
    path('', views.home, name='home'),  # Route pour la page d'accueil
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('graphiques/', views.graphiques, name='graphiques'),
    path('indicators/', views.indicators, name='indicators'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('generate-graph-age/', views.generate_graph_age, name='generate_graph_age'),
    path('generate-graph-cree-par/', views.generate_graph_cree_par, name='generate_graph_cree_par'),
    path('generate-graph-RDVs/', views.generate_graph_RDVs, name='generate_graph_RDVs'),
    path('generate-graph-RDVs-honored/', views.generate_graph_RDVs_honored, name='generate_graph_RDVs_honored'),
    path('generate-indicator-shifts/', views.generate_indicator_shifts, name='generate_indicator_shifts'),
    path('generate-indicator-RDVs/', views.generate_indicator_RDVs, name="generate_indicator_RDVs"),
    path('generate-indicator-RDVs-honored/', views.generate_indicator_RDVs_honored, name="generate_indicator_RDVs_honored")
]
