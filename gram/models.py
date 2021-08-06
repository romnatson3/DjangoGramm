from django.contrib.auth.models import User
from django.db import models
#from cloudinary.models import CloudinaryField
from main.settings import NONAME_AVATAR

# Create your models here.


class Avatar(models.Model):

    class Meta():
        verbose_name = 'avatar'

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatar/', blank=True, default=NONAME_AVATAR)
#    avatar = CloudinaryField('avatar', folder='avatar', blank=True)


class ConfirmEmail(models.Model):

    class Meta():
        verbose_name = 'confirm_email'
        indexes = [
           models.Index(fields=['confirm_email_id']),
        ]

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    confirm_email_id = models.CharField(max_length=256, blank=True, null=True)


class Post(models.Model):

    class Meta():
        verbose_name = 'post'
        indexes = [
           models.Index(fields=['description']),
        ]

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    datetime = models.DateTimeField(auto_now_add=True)
#    photo = CloudinaryField('photo', folder='media', blank=True)
    photo = models.ImageField(upload_to='images/', blank=True)
    description = models.TextField(blank=True, null=True)


class Like(models.Model):

    class Meta():
        verbose_name = 'like'
        unique_together = ('user', 'post')

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, on_delete=models.PROTECT)


class Follow(models.Model):

    class Meta():
        verbose_name = 'follow'
        unique_together = ('follower', 'following')

    follower = models.ForeignKey(User, on_delete=models.PROTECT, related_name='follower', db_column='follower')
    following = models.ForeignKey(User, on_delete=models.PROTECT, related_name='following', db_column='following')
