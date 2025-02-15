import logging
import requests
import io
from django.core.files import File
from django.shortcuts import redirect
from django.views import View
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import login, get_user_model
from gram.models import Avatar


User = get_user_model()


logger = logging.getLogger(__name__)


def get_github_callback_url(request):
    return request.build_absolute_uri('/oauth/github/callback/')


def get_google_callback_url(request):
    return request.build_absolute_uri('/oauth/google/callback/')


class GitHubLoginView(View):
    def get(self, request):
        github_client_id = settings.SOCIAL_AUTH_GITHUB_CLIENT_ID
        github_redirect_uri = get_github_callback_url(request)
        github_scope = 'user:email'
        github_auth_url = (
            f'https://github.com/login/oauth/authorize?client_id={github_client_id}'
            f'&redirect_uri={github_redirect_uri}&scope={github_scope}'
        )
        logger.info(f'Redirecting to {github_auth_url}')
        return redirect(github_auth_url)


class GitHubCallbackView(View):
    def get(self, request):
        code = request.GET.get('code')
        logger.info(f'GitHub code: {code}')
        if not code:
            return HttpResponse('No code provided', status=400)
        token_response = requests.post(
            'https://github.com/login/oauth/access_token',
            headers={'Accept': 'application/json'},
            data={
                'client_id': settings.SOCIAL_AUTH_GITHUB_CLIENT_ID,
                'client_secret': settings.SOCIAL_AUTH_GITHUB_SECRET,
                'code': code,
                'redirect_uri': get_github_callback_url(request)
            }
        )
        token_json = token_response.json()
        logger.info(f'Token response: {token_json}')
        access_token = token_json.get('access_token')
        token_type = token_json.get('token_type')
        if not access_token:
            return HttpResponse('Failed to obtain access token', status=400)

        user_response = requests.get(
            'https://api.github.com/user',
            headers={'Authorization': f'{token_type} {access_token}'}
        )
        logger.info(f'User response: {user_response.json()}')
        user_info = user_response.json()
        avatar_url = user_info.get('avatar_url')
        username = user_info.get('login')
        email = user_info.get('email')
        if not email:
            emails_response = requests.get(
                'https://api.github.com/user/emails',
                headers={'Authorization': f'{token_type} {access_token}'}
            )
            emails = emails_response.json()
            logger.info(f'Emails response: {emails}')
            primary_emails = [e['email'] for e in emails if e.get('primary') and e.get('verified')]
            email = primary_emails[0] if primary_emails else None
        if not email:
            return HttpResponse('Email not available', status=400)
        image = File(
            io.BytesIO(requests.get(avatar_url).content),
            name=f'{username}_avatar.png'
        )
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(username=username, email=email)
            Avatar.objects.create(user=user, avatar=image)
        else:
            user = User.objects.get(email=email)
        login(request, user)
        return redirect('/')


class GoogleLoginView(View):
    def get(self, request):
        auth_url = (
            f'https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
            f'&client_id={settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID}'
            f'&redirect_uri={get_google_callback_url(request)}'
            '&scope=openid email profile&access_type=offline&prompt=consent'
        )
        logger.info(f'Redirecting to {auth_url}')
        return redirect(auth_url)


class GoogleCallbackView(View):
    def get(self, request):
        code = request.GET.get('code')
        logger.info(f'Google code: {code}')
        if not code:
            return HttpResponse('No code provided', status=400)
        token_data = {
            'code': code,
            'client_id': settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID,
            'client_secret': settings.SOCIAL_AUTH_GOOGLE_SECRET,
            'redirect_uri': get_google_callback_url(request),
            'grant_type': 'authorization_code',
        }
        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        token_json = token_response.json()
        logger.info(f'Token response: {token_json}')
        access_token = token_json.get('access_token')
        token_type = token_json.get('token_type')
        if not access_token:
            return HttpResponse('Failed to obtain access token', status=400)
        user_info_response = requests.get(
            'https://openidconnect.googleapis.com/v1/userinfo',
            headers={'Authorization': f'{token_type} {access_token}'}
        )
        user_info = user_info_response.json()
        logger.info(f'User info: {user_info}')
        email = user_info.get('email')
        if not email:
            return HttpResponse('Email not available', status=400)
        username = user_info.get('name')
        avatar_url = user_info.get('picture')
        image = File(
            io.BytesIO(requests.get(avatar_url).content),
            name=f'{username}_avatar.png'
        )
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(username=username, email=email)
            Avatar.objects.create(user=user, avatar=image)
        else:
            user = User.objects.get(email=email)
        login(request, user)
        return redirect('/')
