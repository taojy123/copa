
from django.http import HttpResponseBadRequest, HttpResponse
from django.utils import timezone

from mirror.models import Clipboard


CLIPBOARD_LIMIT_MB = 10


def clipboard(request, token):

    board, created = Clipboard.objects.get_or_create(token=token)

    if request.method == 'GET':
        return HttpResponse(board.content)
    elif request.method == 'POST':
        content = request.POST.get('content')

        if len(content) > 1024 * 1024 * CLIPBOARD_LIMIT_MB:
            return HttpResponseBadRequest(f'the package size must less than {CLIPBOARD_LIMIT_MB}MB')

        board.content = content
        board.save()

        return HttpResponse('set clip success')
    else:
        return HttpResponseBadRequest('method not allow')

