from django.db import models
from django.contrib.auth.models import User


class Token(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField()
    is_valid = models.BooleanField(default=False)


class Req(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    data = models.TextField()
    response = models.TextField(null=True, default=None)
    is_done = models.BooleanField(default=False)
    task = models.CharField(max_length=20)
