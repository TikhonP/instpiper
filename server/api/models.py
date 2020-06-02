from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Token(models.Model):
    name = models.CharField(max_length=50, default='No Name')
    date = models.DateTimeField(('Date'), default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=40)
    is_valid = models.BooleanField(default=False)

    def __str__(self):
        return '{} | {} | {}'.format(self.author, self.name, self.token)


class Proxy(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(('Date'), default=timezone.now)
    proxy = models.TextField()
    name = models.CharField(max_length=50, default='No Name')
    health = models.IntegerField(default=101)

    def __str__(self):
        return '{} | {} | {}...'.format(self.author, self.name, self.proxy[:50])


class Req(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(('Date'), default=timezone.now)
    token = models.ForeignKey(Token, on_delete=models.SET_NULL, null=True)
    data = models.TextField()
    response = models.TextField(null=True, default=None)
    is_done = models.IntegerField(default=0)
    task = models.CharField(max_length=40)
    is_id = models.BooleanField(default=False)
    proxy = models.ForeignKey(Proxy, on_delete=models.SET_NULL, null=True)
    threads = models.IntegerField()

    def __str__(self):
        return '{} | {} | {}'.format(self.author, self.task, self.date)
