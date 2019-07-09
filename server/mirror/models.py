from django.db import models
from django.utils import timezone


class Package(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    content = models.BinaryField(blank=True)
    hash = models.CharField(max_length=50, db_index=True)
    savepoint = models.BooleanField(default=False)
    conflict = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def content_length(self):
        return len(self.content)

