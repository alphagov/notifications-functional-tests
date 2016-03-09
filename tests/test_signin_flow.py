from requests import session

from config import Config
from tests.utils import (retrieve_sms_with_wait,
                         delete_sms_messge,
                         find_csrf_token,
                         get_sms,
                         sign_out,
                         find_page_title
                         )


def test_sign_in_journey():

    try:
        client = session()
        base_url = Config.NOTIFY_ADMIN_URL
        index_resp = client.get(base_url)
        assert index_resp.status_code == 200
        assert 'GOV.UK Notify' == find_page_title(index_resp.text)

        get_sign_resp = client.get(base_url + '/sign-in')
        assert 200 == get_sign_resp.status_code
        assert 'Sign in - GOV.UK Notify'

        token = find_csrf_token(get_sign_resp.text)

        user_name = Config.FUNCTIONAL_TEST_EMAIL
        password = Config.FUNCTIONAL_TEST_PASSWORD
        assert user_name is not None
        data = {'email_address': user_name,
                'password': password,
                'csrf_token': token}
        post_sign_in_resp = client.post(base_url + '/sign-in', data=data,
                                        headers=dict(Referer=base_url+'/sign-in'))
        assert post_sign_in_resp.status_code == 200

        get_two_factor = client.get(base_url + '/two-factor')
        assert get_two_factor.status_code == 200
        assert 'Text verification – GOV.UK Notify' == find_page_title(get_two_factor.text)
        next_token = find_csrf_token(get_two_factor.text)

        # Test will fail if there is not 1 message (we expect only 1 message)
        messages = retrieve_sms_with_wait(user_name)
        assert len(messages) == 1, 'Expecting to retrieve 1 sms message in functional test for user: {}'.format(
            user_name)

        # try to use verify code from message
        m = messages[0]
        two_factor_data = {'sms_code': m.body,
                           'csrf_token': next_token}
        post_two_factor = client.post(base_url + '/two-factor', data=two_factor_data,
                                      headers=dict(Referer=base_url+'/two-factor'))
        assert post_two_factor.status_code == 200
        assert 'Preview' in post_two_factor.text
        assert 'dashboard' in post_two_factor.url
        delete_sms_messge(m.sid)
        sign_out(client, base_url)
    finally:
        # Delete all messages even if the test fails.
        messages = get_sms()
        for m in messages:
            delete_sms_messge(m.sid)
