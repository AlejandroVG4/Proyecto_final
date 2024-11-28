from django.urls import path
from .views import GenerateSasUrlView

urlpatterns = [
    path('get-sas-url/', GenerateSasUrlView.as_view(), name='get_blob_sas'),
]