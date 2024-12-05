from django.urls import path
from .views import GenerateSasUrlView, BusquedaListCreateView, BusquedaDetailView

urlpatterns = [
    path('get-sas-url/', GenerateSasUrlView.as_view(), name='get_blob_sas'),
    path('busquedas/', BusquedaListCreateView.as_view(), name='busqueda-list-create'),
    path('busquedas/<uuid:pk>/', BusquedaDetailView.as_view(), name='busqueda-detail'),
]