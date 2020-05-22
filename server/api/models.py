from django.db import models
from django.contrib.auth.models import User
import datetime


class Token(models.Model):
    date = models.DateTimeField(("Date"), default=datetime.date.today)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField()
    is_valid = models.BooleanField(default=False)


class Req(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(("Date"), default=datetime.date.today)
    token = models.ForeignKey(Token, on_delete=models.SET("Token Deleted"))
    data = models.TextField()
    response = models.TextField(null=True, default=None)
    is_done = models.BooleanField(default=False)
    task = models.CharField(max_length=20)
