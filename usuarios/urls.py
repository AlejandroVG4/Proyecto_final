from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    # TokenObtainPairView
)

urlpatterns = [
    # Ruta para el registro de un nuevo usuario
    path('register/', views.RegisterView.as_view(), name = "sign_up"),
    
    # Ruta para obtener el perfil del usuario autenticado
    path('profile/', views.ProfileView.as_view(), name='user_list'),
    
    # Ruta para obtener, actualizar o eliminar un usuario específico
    path('users/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Ruta para restaurar OJO ES TEMPORAL
    path('users/<str:email>/restore/', views.UserRestoreView.as_view(), name='user_restore'),

    #Authentication
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]
