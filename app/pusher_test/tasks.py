import datetime
import time

import pusher
import random

import requests
from sphere_engine.exceptions import SphereEngineException

from pusher_test.celery import app
from sphere_engine import CompilersClientV3, ProblemsClientV3


@app.task
def send_pusher_judge(source_code, input_data=None):
    import time
    all_start_time = time.time()
    language_id = 11
    hash_code = random.getrandbits(128)

    access_token = "fe52012584bc8c4f04976637af36f6cca35e2b43"
    endpoint = '0c44c635.problems.sphere-engine.com'
    client = ProblemsClientV3(access_token, endpoint)
    pusher_client = pusher.Pusher(
        app_id='569164',
        key='aa225154c5e541e7a10e',
        secret='76d2b29358645c575fb2',
        cluster='ap1',
        ssl=True
    )
    # API usage
    try:
        # ************problem과 testcase를 생성하는 부분********************
        #
        # response = client.problems.create(code='ALBS_004', name='입력값 제곱하기', body="multiply value")
        # problem_code = response['code']
        # testcase1 = client.problems.createTestcase(problemCode=problem_code, _input="3", output="9")
        # testcase2 = client.problems.createTestcase(problemCode=problem_code, _input="4", output="16")
        #
        # result = client.submissions.get(submission_id['id'])
        # # **************************************************************

        status_num = 10000
        create_start_time = time.time()
        print('create_start_time:', create_start_time)
        sphere_id = client.submissions.create(problemCode='ALBS_004', source=source_code,
                                              compilerId=language_id)

        print("---submission create %s seconds ---" % (time.time() - create_start_time))
        print('time.time():', time.time())
        # start_time = time.time()
        subs = client.submissions
        print(dir(subs))

        while status_num != 15:
            get_sub_start_time = time.time()
            # 1.http request로 받아보자 (6.67s , 8.3s, 10.3s.. 왜늘어나지..?)
            # url = "https://{}/api/v3/submissions/{}".format(endpoint, sphere_id['id'])
            # params = {
            #     'access_token': access_token,
            # }
            # response = requests.get(url, params=params)
            # response.raise_for_status()  # requests.HTTPError
            # data = response.json()
            #
            # status = int(data['status'])
            #
            # 2.api로 받아보자 (7~8s...)
            data = subs.get(sphere_id['id'])
            status = int(data['status'])

            print("---submission get status 'no' %s seconds ---" % (time.time() - get_sub_start_time))

            time.sleep(1)

            print('status:', status)
            if status == 15:
                print("---submission get status 'ok' %s seconds ---" % (time.time() - get_sub_start_time))

                # time = result['result_time']
                output = data['result_score']

                # print('total score:', output)
                pusher_client.trigger('my-channel',
                                      'my-event',
                                      {
                                          'output': output,
                                          'acc_percent': 0,
                                          'hash_code': hash_code,
                                      })
                break
        print("---In task %s seconds ---" % (time.time() - all_start_time))


    except SphereEngineException as e:
        if e.code == 401:
            print('Invalid access token')
        elif e.code == 404:
            # aggregates three possible reasons of 404 error
            # non existing problem, compiler or user
            print('Non existing resource (problem, compiler or user), details available in the message: ' + str(e))
        elif e.code == 400:
            print('Empty source code')


@app.task
def send_pusher_compiler(source_code, input_data=None):
    all_start_time = time.time()
    # language_id = 116  # id:11 C /id:4 python / id: 116 python3
    language_id=11
    hash_code = random.getrandbits(128)

    pusher_client = pusher.Pusher(
        app_id='569164',
        key='aa225154c5e541e7a10e',
        secret='76d2b29358645c575fb2',
        cluster='ap1',
        ssl=True
    )

    access_token = 'cba27dc862322761011d7a7a6a4aefde'
    endpoint = '0c44c635.api.compilers.sphere-engine.com'
    client = CompilersClientV3(access_token, endpoint)

    # 1.submission을 생성하고, 0.5 stay
    start_time = time.time()
    r = client.submissions.create(source_code, language_id, input_data)
    submission_id = int(r['id'])
    print('submission_id:', submission_id)
    print("---create time %s seconds ---" % (time.time() - start_time))

    # 2.submission의 결과를 돌려받는다.
    # compiler api문서에는 5초를 기다리라고 했지만 그전에 완료될 수 있음.
    # 1초마다 한번씩 받아와서 compiler는 status가 0이면 성공, problems(judge)는 status가 15면 성공
    status_num = 100
    output = ""
    data = {}

    while status_num != 0:
        start_get_time = time.time()
        data = client.submissions.get(submission_id, withCmpinfo=True, withSource=True, withInput=True, withOutput=True,
                                      withStderr=True)
        print("---get time %s seconds ---" % (time.time() - start_get_time))
        time.sleep(1)
        status = int(data['status'])
        print('status:', status)
        if status == 0:
            output = data['output']
            print("output", output)
            break
        # print("data", data)

    if output:
        acc_percent = 0
        new_keyword = output.replace(" ", "")
        percent = 100 / len(list(new_keyword))
        for i in list(new_keyword):
            acc_percent += percent
            is_loading = False if "%.2f" % acc_percent == "100.00" else True

            if i != " ":
                time.sleep(0.5)
                pusher_client.trigger('my-channel',
                                      'my-event',
                                      {
                                          'output': i,
                                          'acc_percent': "%.2f" % acc_percent,
                                          'hash_code': hash_code,
                                          'is_loading': is_loading
                                      })
    else:
        output = data['cmpinfo']
        print('error_message:', output)
        pusher_client.trigger('my-channel',
                              'my-event',
                              {
                                  'output': output,
                                  'acc_percent': 0,
                                  'hash_code': hash_code,
                              })
    print("---In task %s seconds ---" % (time.time() - all_start_time))
