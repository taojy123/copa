from django.contrib import admin

from mirror.models import Clipboard


@admin.register(Clipboard)
class ClipboardAdmin(admin.ModelAdmin):
    list_display = ['id', 'token', 'content', 'hash', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']

