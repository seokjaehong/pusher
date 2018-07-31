from django.shortcuts import render, redirect

from pusher_test.tasks import send_pusher


def pusher_test(request):
    context = {}
    if request.method == 'GET':
        keyword = request.GET.get('keyword')
        print(keyword)
        if keyword:
            send_pusher.delay(keyword)
            # context = {
            #     'results': keyword,
            # }
        return render(request, 'base.html')
    return redirect('pusher-test')