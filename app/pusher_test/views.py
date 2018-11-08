import time

from django.shortcuts import render

from pusher_test.tasks import send_pusher_compiler, send_pusher_judge


def pusher_test(request):
    if request.method == 'POST':
        start_time = time.time()
        input_data = request.POST.get('input_data')
        source_code = request.POST.get('source_code')
        if source_code:
            if 'compiler' in request.POST:
                # send_pusher_compiler.delay(source_code, input_data)
                start_time = time.time()
                send_pusher_compiler.delay(source_code, input_data)
                print("---In compiler view %s seconds ---" % (time.time() - start_time))
            elif 'judge' in request.POST:
                start_time = time.time()
                send_pusher_judge.delay(source_code, input_data)
                print("---In view %s seconds ---" % (time.time() - start_time))
    return render(request, 'base.html')
