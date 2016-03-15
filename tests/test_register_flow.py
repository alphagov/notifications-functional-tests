import email as email_lib
import imaplib
import uuid

import pytest
from requests import session
from retry import retry

from config import Config
from tests.utils import (find_csrf_token,
                         get_sms_via_heroku,
                         sign_out,
                         remove_all_emails)


def _generate_unique_email(email, uuid_):
    parts = email.split('@')
    return "{}+{}@{}".format(parts[0], uuid_, parts[1])


class RetryException(Exception):
    pass


@retry(RetryException, tries=Config.EMAIL_TRIES, delay=Config.EMAIL_DELAY)
def _get_email_code(email, pwd, email_folder):
    gimap = None
    try:
        gimap = imaplib.IMAP4_SSL('imap.gmail.com')
        try:
            rv, data = gimap.login(email, pwd)
        except imaplib.IMAP4.error:
            pytest.fail("Login to email account has failed.")
        rv, data = gimap.select(email_folder)
        rv, data = gimap.search(None, "ALL")
        ids_count = len(data[0].split())
        if ids_count > 1:
            pytest.fail("There is more than one token email")
        elif ids_count == 1:
            num = data[0].split()[0]
            rv, data = gimap.fetch(num, '(UID BODY[TEXT])')
            msg = email_lib.message_from_bytes(data[0][1])
            gimap.store(num, '+FLAGS', '\\Deleted')
            gimap.expunge()
            return msg.get_payload().strip()
        else:
            raise RetryException("Failed to retrieve the email from the email server.")
    finally:
        if gimap:
            gimap.close()
            gimap.logout()


def test_register_journey():
    '''
    Runs through the register flow creating a new user.
    '''
    remove_all_emails()
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

        next_token = find_csrf_token(post_register_resp.text)
        # sms_code = _get_sms_code(Config.FUNCTIONAL_TEST_EMAIL)
        sms_code = get_sms_via_heroku(client)
        email_code = _get_email_code(
            Config.FUNCTIONAL_TEST_EMAIL,
            Config.FUNCTIONAL_TEST_PASSWORD,
            Config.EMAIL_FOLDER)
    finally:
        remove_all_emails()

    two_factor_data = {'sms_code': sms_code,
                       'email_code': email_code,
                       'csrf_token': next_token}
    post_verify = client.post(base_url + '/verify', data=two_factor_data,
                              headers=dict(Referer=base_url + '/verify'))
    assert post_verify.status_code == 200
    assert 'Which service do you want to set up notifications for?' in post_verify.text
    sign_out(client, base_url)
