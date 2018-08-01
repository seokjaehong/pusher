import time

import pusher
import random
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

    hash_code = random.getrandbits(128)
    new_keyword = keyword.replace(" ", "")
    percent = 100 / len(list(new_keyword))
    acc_percent = 0

    for i in list(new_keyword):
        acc_percent += percent
        is_loading = False if "%.2f" % acc_percent == "100.00" else True

        if i != " ":
            time.sleep(0.6)
            pusher_client.trigger('my-channel',
                                  'my-event',
                                  {
                                      'keyword': i,
                                      'acc_percent': "%.2f" % acc_percent,
                                      'hash_code': hash_code,
                                      'is_loading': is_loading
                                  })
