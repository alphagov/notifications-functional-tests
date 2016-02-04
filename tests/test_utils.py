from tests.utils import retrieve_sms, delete_sms_messge


def test_utils():
    messages = retrieve_sms('rebecca')
    for m in messages:
        print('message: {}, {}, {} {}'.format(m.sid, m.body, m.date_created, m.direction))
        delete_sms_messge(m.sid)

    # delete is not immediate
    # assert len(retrieve_sms('test')) == 0
