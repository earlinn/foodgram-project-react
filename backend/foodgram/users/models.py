from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Class to store users in the database."""

    username = models.CharField(
        'Username',
        max_length=150,
        unique=True,
        null=False,
        blank=False
    )
    email = models.EmailField(
        'Email address',
        max_length=254,
        blank=False,
        null=False,
        unique=True
    )
    first_name = models.CharField(
        'First name',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        'Last name',
        max_length=150,
        blank=False
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Class to store user subscriptions in the database."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Author'
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f'{self.user} is following {self.author}'
