from django.contrib import admin

from mirror.models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'hash', 'savepoint', 'conflict', 'content_length', 'created_at', 'download']
    list_filter = ['name', 'created_at', 'savepoint', 'conflict']

    def download(self, obj):
        return f'<a href="{obj.download}" target="_blank">download</a>'
    download.allow_tags = True
