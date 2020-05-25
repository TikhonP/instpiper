from django.db import models
from django.contrib.auth.models import User
import datetime


class Token(models.Model):
    name = models.CharField(max_length=50, default='No Name')
    date = models.DateTimeField(("Date"), default=datetime.date.today)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=40)
    is_valid = models.BooleanField(default=False)


class Req(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(("Date"), default=datetime.date.today)
    token = models.ForeignKey(Token, on_delete=models.SET_NULL, null=True)
    data = models.TextField()
    response = models.TextField(null=True, default=None)
    is_done = models.IntegerField(default=0)
    task = models.CharField(max_length=40)
