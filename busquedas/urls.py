from django.urls import path
from .views import GenerateSasUrlView, BusquedaListView, BusquedaDetailView, AnalyzeImageView

urlpatterns = [
    path('get-sas-url/', GenerateSasUrlView.as_view(), name='get_blob_sas'),

    # Obtiene las busquedas del usuario logeado
    path('busquedas/', BusquedaListView.as_view(), name='busqueda-list-create'),
    
    path('busquedas/<uuid:pk>/', BusquedaDetailView.as_view(), name='busqueda-detail'),
    path('analyze-image/', AnalyzeImageView.as_view(), name='analyze_image'),
]