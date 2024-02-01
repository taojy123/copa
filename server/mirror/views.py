
from django.http import HttpResponseBadRequest, HttpResponse
from django.utils import timezone

from mirror.models import Clipboard


CLIPBOARD_LIMIT_MB = 10


def clipboard(request, token):

    board, created = Clipboard.objects.get_or_create(token=token)

    if request.method == 'GET':
        target = request.GET.get('target')
        
        if target == 'hash':
            return HttpResponse(board.hash)
        
        return HttpResponse(board.content)
    
    elif request.method == 'POST':
        content = request.POST.get('content')
        hash = request.POST.get('hash') or ''

        if len(content) > 1024 * 1024 * CLIPBOARD_LIMIT_MB:
            return HttpResponseBadRequest(f'the package size must less than {CLIPBOARD_LIMIT_MB}MB')

        board.content = content
        board.hash = hash
        board.save()

        return HttpResponse('set clip success')
    
    else:
        return HttpResponseBadRequest('method not allow')


def clear(request):
    res = Clipboard.objects.filter(content='').delete()
    return HttpResponse(res)
