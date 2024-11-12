from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    # TokenObtainPairView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name = "sign_up"),
    #Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
