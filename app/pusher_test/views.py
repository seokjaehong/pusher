from django.shortcuts import render, redirect

from pusher_test.tasks import send_pusher


def pusher_test(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword')

        if keyword:
            send_pusher.delay(keyword)
        return render(request, 'base.html')
    return redirect('pusher-test')