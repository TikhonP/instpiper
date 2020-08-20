from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()


class TokenV2(models.Model):
    name = models.CharField(max_length=50, default='No Name')
    date_created = models.DateTimeField(('Date'), default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=40)
    is_valid = models.BooleanField(default=False)

    def __str__(self):
        return '{} | {} | {}'.format(self.author, self.name, self.token)


class ProxyV2(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(('Date'), default=timezone.now)
    proxy = models.TextField()
    name = models.CharField(max_length=50, default='No Name')
    health = models.IntegerField(default=101)  # from 0 to 101, 101 - None

    def __str__(self):
        return '{} | {} | {}...'.format(
            self.author, self.name, self.proxy[:50])


class RequestV2(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(('Date'), default=timezone.now)
    token = models.ForeignKey(TokenV2, on_delete=models.SET_NULL, null=True)
    data = models.TextField()
    response = models.TextField(null=True, default=None)
    is_done = models.IntegerField(default=0)  # from 0 to 100
    task_id = models.CharField(max_length=40)
    is_id = models.BooleanField(default=False)
    proxy = models.ForeignKey(ProxyV2, on_delete=models.SET_NULL, null=True)
    threads = models.IntegerField()

    def __str__(self):
        return '{} | {} | {}'.format(self.author, self.task, self.date)
