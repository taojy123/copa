
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django.utils import timezone

from mirror.models import Clipboard


CLIPBOARD_LIMIT_MB = 10


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

    return HttpResponse('set clip success')


def get_clip(request):

    name = request.POST.get('name') or request.GET.get('name')

    if not name:
        return HttpResponseBadRequest('miss name')

    clip = Clipboard.objects.filter(name=name).first()
    if not clip:
        return HttpResponseBadRequest('clip not found')

    return HttpResponse(clip.content)

