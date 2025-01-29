from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import redirect
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from urllib.parse import urlencode
from rest_framework.permissions import IsAuthenticated 

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    
    class CustomOAuth2Client(OAuth2Client):
        def __init__(self, *args, **kwargs):
            if 'scope_delimiter' in kwargs:
                del kwargs['scope_delimiter']
            super().__init__(*args, **kwargs)
            
    client_class = CustomOAuth2Client

    def get(self, request, *args, **kwargs):
        print("\n=== GoogleLoginView.get() ===")
        print(f"Request GET params: {request.GET}")
        
        code = request.GET.get('code')
        if not code:
            print("No authorization code found in request")
            return Response({'error': 'Authorization code not found'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_request = Request(
                request._request,
            )
            new_request._data = {'code': code}
            new_request._full_data = {'code': code}
            new_request._mutable = True
            
            self.request = new_request
            
            print("\nRequest after modification:")
            print(f"Request data: {self.request.data}")
            
            return self.post(new_request, *args, **kwargs)
            
        except Exception as e:
            print(f"\nOAuth error in get(): {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return redirect('http://localhost:3000/auth/login?error=auth_failed')

    def post(self, request, *args, **kwargs):
        print("\n=== GoogleLoginView.post() ===")
        print("GoogleLoginView post method called")


        
        try:
            print("\nRequest details in post:")
            print(f"Request method: {request.method}")
            print(f"Request data: {request.data}")
            
            request._request.method = 'POST'
            
            response = super().post(request, *args, **kwargs)
            print(f"Social login response status code: {response.status_code}")

            if response.status_code == 200:
                try:
                    response_data = response.data
                    print(f"Response data: {response_data}")
                    
                    user = self.user
                    refresh = RefreshToken.for_user(user)
                    print(f"Generated tokens for user: {user}")
                    
                    redirect_path = request.session.get('next_url', '/')
                    print(f"Redirect path: {redirect_path}")
                    
                    frontend_url = f"{settings.REACT_FRONTEND}{redirect_path}"
                    params = {
                        'access_token': str(refresh.access_token),
                        'refresh_token': str(refresh)
                    }
                    redirect_url = f"{frontend_url}?{urlencode(params)}"
                    print(f"Redirect URL: {redirect_url}")
                    
                    return redirect(redirect_url)
                    
                except Exception as inner_e:
                    print(f"Error processing successful response: {str(inner_e)}")
                    raise
            
            print(f"Unexpected response status: {response.status_code}")
            return response
            
        except Exception as e:
            print(f"\nOAuth error in post(): {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return redirect('http://localhost:3000/auth/login?error=auth_failed')

@api_view(['GET'])
def google_oauth_redirect(request):
    print("\n=== google_oauth_redirect() ===")
    print("google_oauth_redirect called")
    
    authorization_url = "https://accounts.google.com/o/oauth2/v2/auth"
    next_path = request.GET.get('from', '/')
    print(f"Next path: {next_path}")
    request.session['next_url'] = next_path

    # Add debug prints
    print("DEBUG SETTINGS:")
    print(f"Direct setting: {settings.GOOGLE_OAUTH_CALLBACK_URL}")
    print(f"From SOCIALACCOUNT_PROVIDERS: {settings.SOCIALACCOUNT_PROVIDERS['google']}")
    
    params = {
        'client_id': settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
        'redirect_uri': settings.GOOGLE_OAUTH_CALLBACK_URL,
        'response_type': 'code',
        'scope': 'email profile',
        'access_type': 'offline',
        'prompt': 'consent',
        'state': next_path
    }
    
    redirect_url = f"{authorization_url}?{urlencode(params)}"
    print(f"Redirect URL: {redirect_url}")
    print(f"Callback URL configured: {settings.GOOGLE_OAUTH_CALLBACK_URL}")
    
    return redirect(redirect_url)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    return Response({
        'id': user.id,
        'email': user.email,
        'username': user.username,
        # Add any other user fields you need
    })