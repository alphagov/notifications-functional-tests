from requests import get, post

from config import Config
from tests.utils import (retrieve_sms_with_wait,
                         delete_sms_messge,
                         get_sms,
                         find_csrf_token
                         )


def test_sign_in_journey():
    try:
        base_url = Config.NOTIFY_ADMIN_URL
        index_resp = get(base_url)
        assert index_resp.status_code == 200
        assert 'GOV.UK Notify' in index_resp.text

        get_sign_resp = get(base_url + '/sign-in',
                            cookies={'notify_admin_session': index_resp.cookies['notify_admin_session']})
        # print('headers: {}'.format(get_reg_resp.headers)) it's possible to assert that headers are set properly here.

        assert 200 == get_sign_resp.status_code
        assert '<p>If you do not have an account, you can <a href="register">register for one now</a>.</p>' in \
               get_sign_resp.text

        token = find_csrf_token(get_sign_resp.text)

        user_name = Config.FUNCTIONAL_TEST_EMAIL
        assert user_name is not None
        data = {'email_address': user_name,
                'password': Config.FUNCTIONAL_TEST_PASSWORD,
                'csrf_token': token}
        post_sign_in_resp = post(base_url + '/sign-in', data=data,
                                 cookies={'notify_admin_session': get_sign_resp.cookies['notify_admin_session']})
        assert post_sign_in_resp.status_code == 200
        assert "We've sent you a text message with a verification code." in post_sign_in_resp.text

        # Test will fail if there is not 1 message (expect only 1 message
        messages = retrieve_sms_with_wait(user_name)
        assert len(messages) == 1, 'Expecting to retrieve 1 sms message in functional test for user: {}'.format(
            user_name)

        # try to use verify code from message
        m = messages[0]
        two_factor_token = find_csrf_token(post_sign_in_resp.text)
        two_factor_data = {'sms_code': m.body,
                           'csrf_token': two_factor_token}
        post_two_factor = post(base_url + '/two-factor', data=two_factor_data,
                               cookies={'notify_admin_session': post_sign_in_resp.cookies['notify_admin_session']})
        assert post_two_factor.status_code == 200
        assert 'GOV.UK Notify | Dashboard' in post_two_factor.text
        assert 'Functional Test Service' in post_two_factor.text
        delete_sms_messge(m.sid)

    finally:
        # Delete all messages even if the test fails.
        messages = get_sms()
        for m in messages:
            delete_sms_messge(m.sid)
