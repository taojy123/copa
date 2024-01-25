import hashlib

from django.db import models
from django.utils import timezone


def md5(content):
    if not content:
        return ''
    return hashlib.md5(content.encode()).hexdigest()


class Clipboard(models.Model):

    token = models.CharField(max_length=100, unique=True)
    content = models.TextField(blank=True)
    hash = models.CharField(max_length=100, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = md5(self.content)
        return super().save(*args, **kwargs)
