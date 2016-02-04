import uuid
from time import sleep

import pytest
from requests import get, post
from config import Config

@pytest.mark.skipif(True, reason='Registration flow is not ready to implement until we have email addresses')
def test_registration_journey():
    base_url = Config.NOTIFY_ADMIN_URL
    index_resp = get(base_url)
    assert index_resp.status_code == 200
    assert 'GOV.UK Notify' in index_resp.text

    get_reg_resp = get(base_url + '/register')
    # print('headers: {}'.format(get_reg_resp.headers)) it's possible to assert that headers are set properly here.

    assert 200 == get_reg_resp.status_code
    assert 'Create an account' in get_reg_resp.text

    user_name = str(uuid.uuid4())
    email = Config.FUNCTION_TEST_EMAIL.format(user_name)

    register_body = {
        'name': user_name,
        'email_address': email,
        'mobile_number': Config.TWILIO_TEST_NUMBER,
        'password': 'validPassword!'
    }
    reg_resp = post(base_url + '/register',
                    json=register_body)

    assert reg_resp.status_code == 200
    assert '''We’ve sent you confirmation codes by email and text message.''' \
           in reg_resp.text

    # Now read the email sent using imaplib
    # Now read the sms
    sleep(5)
    from twilio.rest import TwilioRestClient

    client = TwilioRestClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

    x = 1
    messages = client.messages.list(to="+44 1509 323441")
    while x < 12:
        print("In loop {} times".format(x))
        for m in messages:
            print("verify code: {}".format(m.body))
            break
            # try to verify
            # delete the message
        x += 1
        sleep(5)
        messages = client.messages.list(to=Config.TWILIO_TEST_NUMBER)

        #
        # messages = client.messages.list( to="+44 1509 323441" )
        # for m in messages:
        #     print(m.body)
        #     client.messages.delete(m.sid)
