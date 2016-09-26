import csv
import email as email_lib
import imaplib
import re
import pytest

from retry import retry
from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient
from config import Config
from tests.pages import VerifyPage


def remove_all_emails(email=None, pwd=None, email_folder=None):
    if not email:
        email = Config.FUNCTIONAL_TEST_EMAIL
    if not pwd:
        pwd = Config.FUNCTIONAL_TEST_EMAIL_PASSWORD
    if not email_folder:
        email_folder = Config.EMAIL_FOLDER
    gimap = None
    try:
        gimap = imaplib.IMAP4_SSL('imap.gmail.com')
        rv, data = gimap.login(email, pwd)
        rv, data = gimap.select(email_folder)
        rv, data = gimap.search(None, "ALL")
        for num in data[0].split():
            gimap.store(num, '+FLAGS', '\\Deleted')
            gimap.expunge()
    finally:
        if gimap:
            gimap.close()
            gimap.logout()


def create_temp_csv(number, field_name):
    import os
    import tempfile
    directory_name = tempfile.mkdtemp()
    csv_file_path = os.path.join(directory_name, 'sample.csv')
    with open(csv_file_path, 'w') as csv_file:
        fieldnames = [field_name]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerow({field_name: number})
    return directory_name, 'sample.csv'


class RetryException(Exception):
    pass


@retry(RetryException, tries=Config.EMAIL_TRIES, delay=Config.EMAIL_DELAY)
def get_email_body(profile, email_folder):
    gimap = None
    try:
        gimap = imaplib.IMAP4_SSL('imap.gmail.com')
        try:
            rv, data = gimap.login(profile.email, profile.email_password)
        except imaplib.IMAP4.error as e:
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
            return msg.get_payload().strip().replace('=\r\n', '')  # yikes
        else:
            raise RetryException("Failed to retrieve the email from the email server.")
    finally:
        if gimap:
            gimap.close()
            gimap.logout()


def assert_no_email_present(profile, email_folder):
    gimap = None
    try:
        gimap = imaplib.IMAP4_SSL('imap.gmail.com')
        gimap.login(profile.email, profile.email_password)
        gimap.select(email_folder)
        data = gimap.search(None, "ALL")[1]
        print(data)
        assert len(data[0].split()) == 0
    finally:
        if gimap:
            gimap.close()
            gimap.logout()


def assert_notification_body(notification_id, notification):
    assert notification['id'] == notification_id
    assert 'The quick brown fox jumped over the lazy dog' in notification['body']


def generate_unique_email(email, uuid):
    parts = email.split('@')
    return "{}+{}@{}".format(parts[0], uuid, parts[1])


def get_link(profile, email_label, template_id, email):
    import re
    try:
        email_body = get_notification_via_api(profile.notify_service_id, template_id, profile.env,
                                              profile.notify_service_api_key, email)
        match = re.search('http[s]?://\S+', email_body, re.MULTILINE)
        if match:
            return match.group(0)
        else:
            pytest.fail("Couldn't get the registraion link from the email")
    finally:
        remove_all_emails(email_folder=email_label)


@retry(RetryException, tries=15, delay=Config.EMAIL_DELAY)
def do_verify(driver, profile):
    verify_code = get_verify_code_from_api(profile)
    verify_page = VerifyPage(driver)
    verify_page.verify(verify_code)
    if verify_page.has_code_error():
        raise RetryException


def get_verify_code_from_api(profile):
    verify_code_message = get_notification_via_api(Config.NOTIFY_SERVICE_ID, Config.VERIFY_CODE_TEMPLATE_ID,
                                                   profile.env, Config.NOTIFY_SERVICE_API_KEY, profile.mobile)
    m = re.search('\d{5}', verify_code_message)
    if not m:
        pytest.fail("Could not find the verify code in notification body")
    return m.group(0)


@retry(RetryException, tries=15, delay=Config.EMAIL_DELAY)
def get_notification_via_api(service_id, template_id, env, api_key, sent_to):
    client = NotificationsAPIClient(Config.NOTIFY_API_URL,
                                    service_id,
                                    api_key)
    expected_status = 'sending'if env == 'dev' else 'delivered'
    resp = client.get('notifications', params={'include_jobs': True})
    for notification in resp['notifications']:
        t_id = notification['template']['id']
        to = notification['to']
        status = notification['status']
        if t_id == template_id and to == sent_to and status == expected_status:
            return notification['body']
    else:
        message = 'Could not find notification with template {} to {} with a status of {}' \
            .format(template_id,
                    sent_to,
                    expected_status)
        raise RetryException(message)


def get_email_message(profile, email_label):
    try:
        return get_email_body(profile, email_label)
    finally:
        remove_all_emails(email_folder=email_label)
