import logging
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from gram.models import User, Avatar, ConfirmEmail, Post, Like, Follow
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
import string, random, json
from main.settings import NONAME_AVATAR
from django.db.models import Count
from django.db import IntegrityError
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from gram.mail import send_mail


logger = logging.getLogger(__name__)


def get_random_str():
    str = string.ascii_letters + string.digits
    return ''.join([random.choice(str) for i in range(50)])


@csrf_exempt
def signin(request):
    if request.method == 'POST':
        if request.POST.get('username') and request.POST.get('password'):
            username = request.POST['username'].lower().strip()
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                logger.info(f'User {user.username} is authenticated')
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('home'))
            else:
                logger.warning(f'User {username} is not authenticated')
                return HttpResponse('<h3>Invalid username or password</h3>', status=200)
    return render(request, 'signin.html', {})


@csrf_exempt
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        data = {}
        data['username'] = request.POST.get('username').lower().strip()
        data['email'] = request.POST.get('email')
        data['first_name'] = request.POST.get('first_name')
        data['last_name'] = request.POST.get('last_name')
        data['password'] = request.POST.get('password')
        data['is_active'] = False
        if User.objects.filter(username=data['username']).exists():
            return HttpResponse('<h3>This user already exists</h3>', status=200)
        if User.objects.filter(email=data['email']).exists():
            return HttpResponse('<h3>This email already exists</h3>', status=200)
        user = User.objects.create_user(**data)
        http_host = request.META.get('HTTP_HOST')
        confirm_email_id = get_random_str()
        confirm_email = ConfirmEmail.objects.create(user=user, confirm_email_id=confirm_email_id)
        avatar = Avatar.objects.create(user=user)
        url = f'{request.scheme}://{http_host}/confirm_email/{confirm_email_id}'
        send_mail(
            [user.email],
            f'Please confirm your email address to get full access to DjangoGram.\n {url}',
            'Сonfirm your registration'
        )
        return render(request, 'confirm_email.html', {'email':user.email})


def confirm_email(request, id):
    if request.method == 'GET':
        user = ConfirmEmail.objects.get(confirm_email_id=id).user
        if user and user.is_active == False:
            user.is_active = True
            user.save()
            return redirect(reverse('signin'))
    return HttpResponseNotFound('<h1>Page not found</h1>')


def logoff(request):
    logout(request)
    return redirect(reverse('signin'))


@login_required(login_url='/signin/')
def follow(request, username):
    if request.method == 'GET':
        following = User.objects.filter(username=username).first()
        if following:
            try:
                Follow.objects.create(follower=request.user, following=following)
            except IntegrityError:
                Follow.objects.filter(follower=request.user, following=following).delete()
            return redirect(reverse('profile', args=[following.username]))
    return HttpResponseNotFound('<h1>Page not found</h1>')


def get_posts_list(request, posts):
    posts_list = []
    for i in posts:
        post = {}
        like_count = Like.objects.all().values('post').filter(post=i).annotate(total=Count('post'))
        if like_count:
            post['like_count'] = like_count[0]['total']
        else:
            post['like_count'] = ''
        like = Like.objects.filter(user=request.user, post=i).first()
        if like:
            post['like'] = True
        else:
            post['like'] = False
        post['post_id'] = i.id
        post['username'] = i.user.username
        post['avatar'] = i.user.avatar.avatar.url
        post['bio'] = i.user.avatar.bio
        post['photo'] = i.photo.url
        post['description'] = i.description
        post['datetime'] = i.datetime.strftime('%d.%m.%Y %T')
        posts_list.append(post)
    paginator = Paginator(posts_list, 4)
    cache.set('pages', paginator)
    return paginator.page(1)


def get_user_data(request, username):
    posts_list = []
    data = {}
    user = User.objects.filter(username=username).first()
    if user:
        posts_count = Post.objects.all().values('user').filter(user=user).annotate(total=Count('user'))
        data['posts'] = posts_count[0]['total'] if posts_count else 0
        following = Follow.objects.all().values('follower').filter(follower=user).annotate(total=Count('follower'))
        data['following'] = following[0]['total'] if following else 0
        follower = Follow.objects.all().values('following').filter(following=user).annotate(total=Count('following'))
        data['follower'] = follower[0]['total'] if follower else 0
        posts = Post.objects.filter(user=user).order_by('-datetime')
        posts_list = get_posts_list(request, posts)
    return user, data, posts_list


@login_required(login_url='/signin/')
def profile(request, username):
    user, data, my_posts = get_user_data(request, username)
    if user:
        if Follow.objects.filter(follower=request.user,following=user).exists():
            user.follow = True
        else:
            user.follow = False

        if request.method == 'GET':
            return render(request, 'profile.html', {'user':user, 'data':data, 'posts_list':my_posts})

        if request.method == 'POST':
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.save()
            avatar = Avatar.objects.filter(user=user).first()
            if not avatar:
                avatar = Avatar(user=user)
            photo = request.FILES.get('avatar')
            if photo:
                avatar.avatar = photo
            bio = request.POST.get('bio')
            if bio:
                avatar.bio = bio
            avatar.save()
            return render(request, 'profile.html', {'user':user})
    return HttpResponseNotFound('<h1>Page not found</h1>')


@login_required(login_url='/signin/')
def home(request):
    if request.method == 'GET':
        posts_list = []
        user, data, my_posts = get_user_data(request, request.user.username)
        my_post = request.GET.get('my_post')
        if not my_post:
            posts = []
            follow = Follow.objects.filter(follower=user)
            if follow:
                for i in follow:
                    post = Post.objects.filter(user=i.following)
                    if post:
                        posts.extend(post)
            posts.sort(key=lambda x: x.datetime, reverse=True)
            posts_list = get_posts_list(request, posts)
        else:
            posts_list = my_posts

    search = request.GET.get('search')
    if search:
        posts_list = []
        search = search.strip()
        result = Post.objects.filter(description__icontains=search)
        if result:
            posts_list = get_posts_list(request, result)
    return render(request, 'home.html', {'posts_list':posts_list, 'data':data, 'user':user})


@login_required(login_url='/signin/')
def add_post(request):
    user = request.user
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        if photo:
            description = request.POST.get('description')
            post = Post(user=user, photo=photo, description=description)
            post.save()
    return render(request, 'add_post.html', {})


@login_required()
def like(request):
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {}
            post_id = json.load(request).get('post_id')
            user = request.user
            post = Post.objects.filter(id=post_id).first()
            if post:
                try:
                    like = Like.objects.create(user=user, post=post)
                except IntegrityError:
                    Like.objects.get(user=user, post=post).delete()
            like_count = Like.objects.all().values('post').filter(post=post).annotate(total=Count('post'))
            if like_count:
                data['like_count'] = like_count[0]['total']
            else:
                data['like_count'] = None
            like = Like.objects.filter(user=request.user, post=post).first()
            data['like'] = True if like else False
            return JsonResponse(data)
    return HttpResponseNotFound()


@login_required()
def scroll(request):
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            page = json.load(request).get('page')
            paginator = cache.get('pages')
            if paginator:
                if page <= paginator.num_pages:
                    return JsonResponse(list(paginator.page(page)), safe=False)
    return HttpResponseNotFound()
