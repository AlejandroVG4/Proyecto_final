from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    # TokenObtainPairView
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Ruta para registrar un nuevo usuario en la aplicación.
    path('registro/', views.RegisterView.as_view(), name = "sign_up"),

    # Ruta para obtener los datos del perfil del usuario autenticado.
    path('perfil/', views.ProfileView.as_view(), name='user_list'),

    # Ruta para actualizar o eliminar un usuario específico.
    path('detalle/', views.UserDetailView.as_view(), name='user_detail'),

    # Autenticación
    # Ruta para obtener un par de tokens (access y refresh) para la autenticación del usuario.
    path('token/obtener/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Ruta para renovar el token de acceso utilizando un token de actualización válido.
    path('token/renovar/', TokenRefreshView.as_view(), name='token_refresh'),

    # Rutas para gestionar el proceso de recuperación de contraseñas
    # Ruta para solicitar envio email de restablecimiento contraseña
    path('contrasena/restablecer/',views.CustomPasswordResetView.as_view(), name='password_reset'),

    # Ruta para verificar la validez del UID y token para el restablecimiento de contraseña.
    path('contrasena/restablecer/confirmar/<str:uidb64>/<str:token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Ruta para guardar la nueva contraseña
    path('nueva-contrasena/<str:uidb64>/<str:token>/', views.SetNewPasswordView.as_view(), name='password_reset_complete'),

    # Ruta para redirigir a vista redirije al DeepLink o pagina auxiliar
    path('redirigir/<str:uidb64>/<str:token>/', views.RedirectToDeepLink, name='redirect_to_deep_link'),

    #Ruta de fallback para restablecimiento de contraseña.
    path("fallback/contrasena/restablecer/<str:uidb64>/<str:token>/", views.PasswordResetFallbackView, name="password_reset_fallback"),
    
    # Ruta para cerrar sesión
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Ruta para cambiar contraseña usuario 
    #path('update-password/', views.PasswordUpdateView.as_view(), name='update_password'),

    # Ruta para verificar la contraseña actual (antigua) del usuario antes de permitir un cambio de contraseña.
    path("password/verify-old/", views.VerifyOldPasswordView.as_view(), name="verify_old_password"),
]
