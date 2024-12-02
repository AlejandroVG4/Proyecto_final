from django.urls import path
from .views import GenerateSasUrlView, AnalyzeImageView

urlpatterns = [
    path('get-sas-url/', GenerateSasUrlView.as_view(), name='get_blob_sas'),
    path('analyze-image/', AnalyzeImageView.as_view(), name='analyze_image'),
]