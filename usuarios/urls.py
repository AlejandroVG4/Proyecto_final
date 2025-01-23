from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    # TokenObtainPairView
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Ruta para el registro de un nuevo usuario
    path('registro/', views.RegisterView.as_view(), name = "sign_up"),

    # Ruta para obtener el perfil del usuario autenticado
    path('perfil/', views.ProfileView.as_view(), name='user_list'),

    # Ruta para obtener, actualizar o eliminar un usuario específico
    path('detalle/', views.UserDetailView.as_view(), name='user_detail'),

    #Authentication
    path('token/obtener', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/renovar', TokenRefreshView.as_view(), name='token_refresh'),

    #Rutas para recuperar contraseñas
    # URL para solicitar envio email de restablecimiento contraseña
    path('contrasena/restablecer',views.CustomPasswordResetView.as_view(), name='password_reset'),
    path(
        'password-reset/done/',  # URL que indica que el correo fue enviado
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',  # URL con el token para restablecer la contraseña
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'password-reset-complete/',  # URL que indica que la contraseña ha sido cambiada
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),
]
