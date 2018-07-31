import time

import pusher

from pusher_test.celery import app


@app.task
def send_pusher(keyword):
    pusher_client = pusher.Pusher(
        app_id='569164',
        key='aa225154c5e541e7a10e',
        secret='76d2b29358645c575fb2',
        cluster='ap1',
        ssl=True
    )
    print('keyword:',keyword)
    for i in list(keyword):
        print(i)
        # if i != " ":
        time.sleep(0.5)
        pusher_client.trigger('my-channel', 'my-event', i)

