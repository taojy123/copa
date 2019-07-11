import hashlib
from io import BytesIO

from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseNotFound, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404

from mirror.models import Package


PACKAGE_LIMIT_MB = 100


def status(request):
    name = request.POST.get('name')
    savepoint = request.POST.get('savepoint', False)
    conflict = request.POST.get('conflict', False)
    latest = request.POST.get('latest', False)
    packages = Package.objects.filter(name=name).order_by('-id')
    if savepoint:
        packages = packages.filter(savepoint=True)
    if conflict:
        packages = packages.filter(conflict=True)
    if latest:
        packages = packages[:1]
    rs = []
    for package in packages:
        r = {
            'id': package.id,
            'name': package.name,
            'content_length': package.content_length,
            'hash': package.hash,
            'savepoint': package.savepoint,
            'conflict': package.conflict,
            'created_at': package.created_at,
        }
        rs.append(r)
    return JsonResponse({'packages': rs})


def push(request):
    name = request.POST.get('name')
    hash = request.POST.get('hash')
    savepoint = request.POST.get('savepoint')
    package = request.FILES.get('package')

    if not name:
        return HttpResponseBadRequest('miss name')


    packages = Package.objects.filter(name=name).order_by('-id')

    p = packages.filter(hash=hash).first()

    if p and not savepoint:
        return HttpResponse('package exists')

    if not p:
        if not package:
            return HttpResponseBadRequest('miss package')
        content = package.read()
        if len(content) > 1024 * 1024 * PACKAGE_LIMIT_MB:
            return HttpResponseBadRequest(f'the package size must less than {PACKAGE_LIMIT_MB}MB')
        if hashlib.md5(content).hexdigest() != hash:
            return HttpResponseBadRequest('hash not match')
        p = Package.objects.create(name=name, hash=hash, content=content)

    if savepoint:
        p.savepoint = True
        p.save(update_fields=['savepoint'])

    return HttpResponse('package saved')


def pull(request):
    name = request.POST.get('name')
    hash = request.POST.get('hash')
    if hash:
        package = Package.objects.filter(name=name, hash=hash).first()
    else:
        package = Package.objects.filter(name=name).order_by('-id').first()
    if not package:
        return HttpResponseNotFound('package not found')
    content = BytesIO(package.content)
    return StreamingHttpResponse(content)




