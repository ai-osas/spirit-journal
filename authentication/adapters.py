# authentication/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from rest_framework_simplejwt.tokens import RefreshToken

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Called before the social login is processed.
        Here we can modify the social login process if needed.
        """
        user = sociallogin.user
        if user.id:
            # User already exists, update their Google ID if needed
            if not user.google_id and sociallogin.account.provider == 'google':
                user.google_id = sociallogin.account.uid
                user.save()
        return super().pre_social_login(request, sociallogin)

    def populate_user(self, request, sociallogin, data):
        """
        Called when creating a new user from social login.
        """
        user = super().populate_user(request, sociallogin, data)
        if sociallogin.account.provider == 'google':
            user.google_id = sociallogin.account.uid
        return user

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_response_data(self, request, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'is_premium': user.is_premium,
            }
        }