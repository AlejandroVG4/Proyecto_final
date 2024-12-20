from django.urls import path
from .views import GenerateSasUrlView, BusquedaListView, BusquedaDetailView, AnalyzeImageView

urlpatterns = [
    # Obtiene las busquedas del usuario logeado
    path('', BusquedaListView.as_view(), name='busqueda-list-create'),
    # Genera Token SAS
    path('get-sas-url/', GenerateSasUrlView.as_view(), name='get_blob_sas'),
    # Analizar la imagen y crear la busqueda
    path('analyze-image/', AnalyzeImageView.as_view(), name='analyze_image'),
    # Obtener una búsqueda por su id
    path('<uuid:pk>/', BusquedaDetailView.as_view(), name='busqueda-detail')
]