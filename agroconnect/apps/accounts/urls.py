from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/',         views.RegisterView.as_view(),       name='register'),
    path('login/',            views.LoginView.as_view(),          name='login'),
    path('logout/',           views.LogoutView.as_view(),         name='logout'),
    path('verify/<str:token>/', views.VerifyEmailView.as_view(),  name='verify'),
    path('dashboard/',        views.DashboardView.as_view(),      name='dashboard'),
    path('profile/',          views.ProfileUpdateView.as_view(),  name='profile'),
    path('password-reset/',   views.PasswordResetView.as_view(),  name='password_reset'),
    path('debug-auth-x9k2/',  views.DebugAuthView.as_view(),      name='debug_auth'),
]