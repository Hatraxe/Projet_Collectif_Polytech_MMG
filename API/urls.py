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
    path('generate-graph-age/', views.generate_graph_age, name='generate_graph_age'),
    path('generate-graph-cree-par/', views.generate_graph_cree_par, name='generate_graph_cree_par'),
    path('generate-graph-RDV/', views.generate_graph_RDV, name='generate_graph_RDV'),
    path('generate-graph-RDV-honored/', views.generate_graph_RDV_honored, name='generate_graph_RDV_honored'),
    path('generate-indicator-shifts/', views.generate_indicator_shifts, name='generate_indicator_shifts'),
    path('generate-indicator-RDV/', views.generate_indicator_RDV, name="generate_indicator_RDV"),
    path('generate-indicator-RDV-honored/', views.generate_indicator_RDV_honored, name="generate_indicator_RDV_honored"),
    path('generate-indicator-distribution-of-RDV/', views.generate_indicator_distribution_of_RDV, name="generate_indicator_distribution_of_RDV"),
    path('generate-indicator-statut/', views.generate_indicator_statut, name="generate_indicator_statut"),
    path('generate-indicator-RDV-made-covered/', views.generate_indicator_RDV_made_covered, name="generate_indicator_RDV_made_covered"),
    path('generate-indicator-breakdown-of-times-workday/', views.generate_indicator_breakdown_of_times_workday, name="generate_indicator_breakdown_of_times_workday"),
    path('generate-indicator-breakdown-of-times-weekend-holiday/', views.generate_indicator_breakdown_of_times_weekend_holiday, name="generate_indicator_breakdown_of_times_weekend_holiday")
]
