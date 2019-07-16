from django.contrib import admin

from mirror.models import Package, Clipboard


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'hash', 'savepoint', 'conflict', 'created_at', 'download']
    list_filter = ['name', 'created_at', 'savepoint', 'conflict']


@admin.register(Clipboard)
class ClipboardAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'content', 'created_at', 'updated_at']
    list_filter = ['name', 'created_at', 'updated_at']

