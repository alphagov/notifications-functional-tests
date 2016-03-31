from requests import session

from config import Config
from tests.utils import (find_csrf_token,
                         get_sms_via_heroku,
                         sign_out,
                         find_page_title
                         )


def test_sign_in_journey():
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

    # Test will fail if there is no sms_code delivered after 12 attempts
    sms_code = get_sms_via_heroku(client)

    # try to use verify code from message
    two_factor_data = {'sms_code': sms_code,
                       'csrf_token': next_token}
    post_two_factor = client.post(base_url + '/two-factor', data=two_factor_data,
                                  headers=dict(Referer=base_url + '/two-factor'))
    assert post_two_factor.status_code == 200

    assert Config.ENVIRONMENT.capitalize() in post_two_factor.text
    assert 'dashboard' in post_two_factor.url
    sign_out(client, base_url)
