from django.test import TestCase, Client
from django.core import mail
from gram.models import User, Avatar, ConfirmEmail, Post, Like, Follow
from django.urls import reverse
from django.contrib.auth import login
from main.settings import NONAME_AVATAR
from django.db.models import Count


class TestView(TestCase):
    def setUp(self):
        self.test = User.objects.create_user(username='test', password='test', is_active=True)
        Avatar.objects.create(user=self.test)
        self.post = Post.objects.create(user=self.test, photo=NONAME_AVATAR)
        self.test2 = User.objects.create_user(username='test2', password='test2', is_active=True)
        Avatar.objects.create(user=self.test2)
        self.post2 = Post.objects.create(user=self.test2, photo=NONAME_AVATAR)
        self.test3 = User.objects.create_user(username='test3', password='test3', is_active=True)
        Avatar.objects.create(user=self.test3)
        self.post3 = Post.objects.create(user=self.test3, photo=NONAME_AVATAR)
        self.client = Client()
        self.url_profile_test = reverse('profile', args=['test'])
        self.url_profile_test2 = reverse('profile', args=['test2'])
        self.url_register = reverse('register')
        self.url_home = reverse('home')
        self.url_add_post = reverse('add_post')
        self.url_like_post3 = reverse('like', args=[self.post3.id])
        self.url_follow_test3 = reverse('follow', args=[self.test3.username])


    def tearDown(self):
        pass


    def test_profile(self):
        signin = self.client.login(username='test', password='test')
        self.assertEqual(signin, True)

        response = self.client.get(self.url_profile_test2)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            self.url_profile_test, {'first_name':'First Name', 'last_name':'Last Name', 'bio':'Bio'})
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='test')
        avatar = Avatar.objects.get(user=user)
        self.assertEqual(user.first_name, 'First Name')
        self.assertEqual(user.last_name, 'Last Name')
        self.assertEqual(avatar.bio, 'Bio')


    def test_add_post(self):
        signin = self.client.login(username='test', password='test')
        self.assertEqual(signin, True)
        response = self.client.post(
            self.url_add_post, {'photo':'noname.png', 'description':'Photo description'})
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='test')
        posts = Post.objects.filter(user=user)
        self.assertGreater(len(posts), 0)


    def test_home(self):
        signin = self.client.login(username='test', password='test')
        self.assertEqual(signin, True)
        response = self.client.get(self.url_home)
        self.assertEqual(response.status_code, 200)
        self.assertIn('test', response.content.decode())


    def test_register_and_mail_send(self):
        response = self.client.post(
            self.url_register, {'first_name':'First Name', 'username':'test4',
                                'password': 'test4', 'email':'roman@rns.pp.ua',
                                'last_name':'Last Name'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        user = User.objects.get(username='test3')
        user.is_active = True
        user.save()
        signin = self.client.login(username='test3', password='test3')
        self.assertEqual(signin, True)


    def test_like(self):
        headers = {'HTTP_REFERER': self.url_home}
        signin = self.client.login(username='test', password='test')
        response = self.client.get(self.url_like_post3, **headers)
        signin = self.client.login(username='test2', password='test2')
        response = self.client.get(self.url_like_post3, **headers)
        like = Like.objects.all().values('post').filter(post=self.post3).annotate(total=Count('post'))
        like_count = like[0]['total']
        self.assertEqual(like_count, 2)


    def test_follow(self):
        signin = self.client.login(username='test', password='test')
        response = self.client.get(self.url_follow_test3)
        signin = self.client.login(username='test2', password='test2')
        response = self.client.get(self.url_follow_test3)
        follower = Follow.objects.all().values('following').filter(following=self.test3).annotate(total=Count('following'))[0]['total']
        self.assertEqual(follower, 2)
