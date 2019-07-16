import hashlib
from io import BytesIO

from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseNotFound, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from mirror.models import Package, Clipboard

PACKAGE_LIMIT_MB = 100
CLIPBOARD_LIMIT_MB = 5


def status(request):
    name = request.POST.get('name') or request.GET.get('name')
    savepoint = request.POST.get('savepoint') or request.GET.get('savepoint')
    conflict = request.POST.get('conflict') or request.GET.get('conflict')
    latest = request.POST.get('latest') or request.GET.get('latest')
    limit = int(request.POST.get('limit') or request.GET.get('limit') or 0)
    packages = Package.objects.filter(name=name).order_by('-id')
    if savepoint:
        packages = packages.filter(savepoint=True)
    if conflict:
        packages = packages.filter(conflict=True)
    if latest:
        limit = 1
    if limit:
        packages = packages[:limit]
    rs = []
    for package in packages:
        r = {
            'id': package.id,
            'name': package.name,
            'hash': package.hash,
            'savepoint': package.savepoint,
            'conflict': package.conflict,
            'created_at': timezone.localtime(package.created_at),
            'content_length': '-',  # todo: deprecated to remove
        }
        rs.append(r)
    return JsonResponse({'packages': rs})


def push(request):
    name = request.POST.get('name')
    hash = request.POST.get('hash')
    savepoint = request.POST.get('savepoint')
    package = request.FILES.get('package')

    savepoint = bool(savepoint)

    if not name:
        return HttpResponseBadRequest('miss name')

    if not package:
        return HttpResponseBadRequest('miss package')

    content = package.read()
    if len(content) > 1024 * 1024 * PACKAGE_LIMIT_MB:
        return HttpResponseBadRequest(f'the package size must less than {PACKAGE_LIMIT_MB}MB')

    p = Package.objects.filter(name=name).order_by('-id').first()

    if p and p.hash == hash and not savepoint:
        return JsonResponse({'status': 'exists'})

    # if hashlib.md5(content).hexdigest() != hash:
    #     return HttpResponseBadRequest('hash not match')

    Package.objects.create(name=name, hash=hash, content=content, savepoint=savepoint)

    return JsonResponse({'status': 'saved'})


def pull(request):
    name = request.POST.get('name') or request.GET.get('name')
    hash = request.POST.get('hash') or request.GET.get('hash')
    if hash:
        package = Package.objects.filter(name=name, hash=hash).first()
    else:
        package = Package.objects.filter(name=name).order_by('-id').first()
    if not package:
        return HttpResponseNotFound('package not found')
    content = BytesIO(package.content)
    return StreamingHttpResponse(content, content_type='application/zip')


def set_clip(request):
    name = request.POST.get('name') or request.GET.get('name')
    content = request.POST.get('content') or request.GET.get('content')

    if not name or not content:
        return HttpResponseBadRequest('miss name or content')

    if len(content) > 1024 * 1024 * CLIPBOARD_LIMIT_MB:
        return HttpResponseBadRequest(f'the package size must less than {CLIPBOARD_LIMIT_MB}MB')

    clip, created = Clipboard.objects.get_or_create(name=name)
    clip.content = content
    clip.save()

    return JsonResponse({'status': 'set clip success'})


def get_clip(request):
    name = request.POST.get('name') or request.GET.get('name')

    if not name:
        return HttpResponseBadRequest('miss name')

    clip = Clipboard.objects.filter(name=name).first()
    if not clip:
        return HttpResponseBadRequest('clip not found')

    return JsonResponse({'content': clip.content})


def clear(request):
    names = Package.objects.all().values_list('name', flat=True).distinct()
    for name in set(names):
        latest = Package.objects.filter(name=name).latest('id')
        latest_id = latest.id if latest else 0
        Package.objects.filter(name=name).exclude(id=latest_id).exclude(savepoint=True).exclude(conflict=True).delete()
    return HttpResponse({'status': 'cleaned'})



