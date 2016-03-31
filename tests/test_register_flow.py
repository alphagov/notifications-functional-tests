import uuid

import pytest
from requests import session
from bs4 import BeautifulSoup

from config import Config
from tests.utils import (find_csrf_token,
                         get_sms_via_heroku,
                         sign_out,
                         remove_all_emails,
                         get_email_body)


def _generate_unique_email(email, uuid_):
    parts = email.split('@')
    return "{}+{}@{}".format(parts[0], uuid_, parts[1])


def _get_registration_link(email_body):
    import re
    match = re.search('http[s]?://\S+', email_body)
    if match:
        return match.group(0)
    else:
        return None


def test_register_journey():
    '''
    Runs through the register flow creating a new user.
    '''
    remove_all_emails(email_folder=Config.REGISTRATION_EMAIL_LABEL)
    client = session()
    base_url = Config.NOTIFY_ADMIN_URL
    index_resp = client.get(base_url)
    # Check the site is up and running
    assert index_resp.status_code == 200

    get_register_resp = client.get(base_url + '/register')

    assert 200 == get_register_resp.status_code

    token = find_csrf_token(get_register_resp.text)

    uuid_ = uuid.uuid1()
    email = _generate_unique_email(Config.FUNCTIONAL_TEST_EMAIL, uuid_)
    data = {'name': str(uuid_),
            'email_address': email,
            'mobile_number': Config.TWILIO_TEST_NUMBER,
            'password': Config.FUNCTIONAL_TEST_PASSWORD,
            'csrf_token': token}
    # Redirects followed
    try:
        post_register_resp = client.post(base_url + '/register', data=data,
                                         headers=dict(Referer=base_url + '/register'))
        assert post_register_resp.status_code == 200

        email_body = get_email_body(
            Config.FUNCTIONAL_TEST_EMAIL,
            Config.FUNCTIONAL_TEST_PASSWORD,
            Config.REGISTRATION_EMAIL_LABEL)
    finally:
        remove_all_emails(email_folder=Config.REGISTRATION_EMAIL_LABEL)

    registration_link = _get_registration_link(email_body)
    if not registration_link:
        pytest.fail("Couldn't get the registraion link from the email")

    resp = client.get(registration_link)
    resp.raise_for_status()
    assert resp.url == base_url + '/verify'

    sms_code = get_sms_via_heroku(client)
    next_token = find_csrf_token(resp.text)

    two_factor_data = {'sms_code': sms_code,
                       'csrf_token': next_token}

    post_verify = client.post(base_url + '/verify', data=two_factor_data,
                              headers=dict(Referer=base_url + '/verify'))
    assert post_verify.status_code == 200

    page = BeautifulSoup(post_verify.text, 'html.parser')
    assert page.h1.string.strip() == 'When people receive notifications, who should they be from?'
    sign_out(client, base_url)
