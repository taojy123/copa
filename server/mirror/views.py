import hashlib
from io import BytesIO

from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseNotFound, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404

from mirror.models import Package


PACKAGE_LIMIT_MB = 100


def push(request):
    name = request.POST.get('name')
    hash = request.POST.get('hash')
    savepoint = request.POST.get('savepoint')
    package = request.FILES.get('package')

    if not name:
        return HttpResponseBadRequest('miss name')

    if not package:
        return HttpResponseBadRequest('miss package')

    packages = Package.objects.filter(name=name).order_by('-id')

    package = packages.filter(hash=hash).first()

    if package and not savepoint:
        return HttpResponse('package exists')

    if not package:
        content = package.read()
        if len(content) > 1024 * 1024 * PACKAGE_LIMIT_MB:
            return HttpResponseBadRequest(f'the package size must less than {PACKAGE_LIMIT_MB}MB')
        if hashlib.md5(content).hexdigest() != hash:
            return HttpResponseBadRequest('hash not match')
        package = Package.objects.create(name=name, hash=hash, content=content)

    if savepoint:
        package.savepoint = True
        package.save(update_fields=['savepoint'])

    return HttpResponse('package saved')


def fetch(request):
    name = request.POST.get('name')
    package = Package.objects.filter(name=name).order_by('-id').first()
    if not package:
        return HttpResponseNotFound('package not exists')
    content = BytesIO(package.content)
    return StreamingHttpResponse(content)


def savepoints(request):
    name = request.POST.get('name')
    packages = Package.objects.filter(name=name, savepoint=True).order_by('-id')
    rs = []
    for package in packages:
        r = {
            'id': package.id,
            'name': package.name,
            'content_length': package.content_length,
            'hash': package.hash,
            'created_at': package.created_at,
        }
        rs.append(r)
    return JsonResponse({'savepoints': rs})


def loadpoint(request):
    name = request.POST.get('name')
    hash = request.POST.get('hash')
    package = Package.objects.filter(name=name, hash=hash).first()
    if not package:
        return HttpResponseNotFound('package not found')
    content = BytesIO(package.content)
    return StreamingHttpResponse(content)



