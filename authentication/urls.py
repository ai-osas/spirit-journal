# authentication/urls.py
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import GoogleLoginView, google_oauth_redirect, get_user_profile

urlpatterns = [
    path('', include('dj_rest_auth.urls')),
    path('registration/', include('dj_rest_auth.registration.urls')),
    path('google/login/', google_oauth_redirect, name='google_login'),
    path('google/callback/', GoogleLoginView.as_view(), name='google_callback'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', get_user_profile, name='user-profile'),
]