"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from gram.views import signin, home, register, confirm_email, profile, logoff, add_post, follow, like, scroll
from django.conf import settings
from django.views.static import serve
from django.contrib.auth import logout
from gram.oauth import GitHubLoginView, GitHubCallbackView, GoogleLoginView, GoogleCallbackView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signin/', signin, name='signin'),
    path('logoff/', logoff, name='logoff'),
    path('register/', register, name='register'),
    path('', home, name='home'),
    path('add_post/', add_post, name='add_post'),
    re_path(r'profile/(?P<username>\w*)$', profile, name='profile'),
    re_path(r'^confirm_email/(?P<id>.{50})$', confirm_email, name='confirm_email'),
    re_path(r'^follow/(?P<username>\w*)$', follow, name='follow'),
    path('like/', like, name='like'),
    path('scroll/', scroll, name='scroll'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('oauth/github/login/', GitHubLoginView.as_view(), name='github_login'),
    path('oauth/github/callback/', GitHubCallbackView.as_view(), name='github_callback'),
    path('oauth/google/login/', GoogleLoginView.as_view(), name='google_login'),
    path('oauth/google/callback/', GoogleCallbackView.as_view(), name='google_callback'),
]
