from django.test import TestCase
from gram.models import User, Avatar, ConfirmEmail, Post, Like, Follow
from main.settings import NONAME_AVATAR


class TestModel(TestCase):
    def setUp(self):
        test = User.objects.create(username='test', first_name='test')
        Avatar.objects.create(user=test)
        post = Post.objects.create(user=test, photo=NONAME_AVATAR)
        test2 = User.objects.create(username='test2', first_name='test2')
        Avatar.objects.create(user=test2)
        post2 = Post.objects.create(user=test2, photo=NONAME_AVATAR)
        Like.objects.create(user=test, post=post2)
        Like.objects.create(user=test2, post=post)
        Follow.objects.create(follower=test, following=test2)
        Follow.objects.create(follower=test2, following=test)


    def tearDown(self):
        pass


    def test_avatar_name_label(self):
        avatar = Avatar.objects.first()
        field_label = avatar._meta.get_field('avatar').verbose_name
        self.assertEquals(field_label, 'avatar')


    def test_post_name_label(self):
        post = Post.objects.first()
        field_label = post._meta.get_field('photo').verbose_name
        self.assertEquals(field_label, 'photo')


    def test_object_id(self):
        avatar = Avatar.objects.get(id=1)
        post = Avatar.objects.get(id=1)
        self.assertEquals(avatar.user, post.user)


    def test_like(self):
        like = Like.objects.first()
        field1 = like._meta.get_field('user').verbose_name
        field2 = like._meta.get_field('post').verbose_name
        self.assertEqual(field1, 'user')
        self.assertEqual(field2, 'post')


    def test_follow(self):
        follow = Follow.objects.first()
        field1 = follow._meta.get_field('follower').verbose_name
        field2 = follow._meta.get_field('following').verbose_name
        self.assertEqual(field1, 'follower')
        self.assertEqual(field2, 'following')
