from django.db import models
from django.utils import timezone


class Clipboard(models.Model):

    token = models.CharField(max_length=100, unique=True)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

