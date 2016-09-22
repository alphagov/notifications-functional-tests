import csv
import email as email_lib
import imaplib
import re
from datetime import datetime

import pytest
from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient
from retry import retry

from config import Config
from tests.pages import VerifyPage


class RetryException(Exception):
    pass


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


def assert_notification_body(client, message, notification_id):
    assert "The quick brown fox jumped over the lazy dog" in message["body"]
    resp_json = client.get_notification_by_id(notification_id)
    assert resp_json['data']['notification']['id'] == notification_id


@retry(RetryException, tries=Config.EMAIL_TRIES, delay=Config.EMAIL_DELAY)
def get_delivered_notification(client, notification_id, expected_status):
    """
    Waits until a notification is the expected, and then returns its response json.

    Warning! Will fail after waiting ~3 minutes if:
    * the notification doesn't get sent (eg celery not running)
    * you run with a regular (non research-mode or test api key) client!

    """
    try:
        resp_json = client.get_notification_by_id(notification_id)
    except HTTPError as e:
        if e.status_code == 404:
            raise RetryException('Notification not created yet')
        else:
            raise

    status = resp_json['data']['notification']['status']
    if status != expected_status:
        raise RetryException('Notification still in {}'.format(status))
    assert status == expected_status
    return resp_json['data']['notification']


def generate_unique_email(email, uuid):
    parts = email.split('@')
    return "{}+{}@{}".format(parts[0], uuid, parts[1])


def get_link(profile, email_label, template_id, email, expected_created_at):
    import re
    try:
        email_body = get_notification_via_api(profile.notify_service_id, template_id, profile.env,
                                              profile.notify_service_api_key, email, expected_created_at)
        match = re.search('http[s]?://\S+', email_body, re.MULTILINE)
        if match:
            return match.group(0)
        else:
            pytest.fail("Couldn't get the registraion link from the email")
    finally:
        remove_all_emails(email_folder=email_label)


@retry(RetryException, tries=15, delay=Config.EMAIL_DELAY)
def do_verify(driver, profile, expected_created_at):
    verify_code = get_verify_code_from_api(profile, expected_created_at)
    verify_page = VerifyPage(driver)
    verify_page.verify(verify_code)
    if verify_page.has_code_error():
        raise RetryException


def get_verify_code_from_api(profile, expected_created_at):
    verify_code_message = get_notification_via_api(Config.NOTIFY_SERVICE_ID, Config.VERIFY_CODE_TEMPLATE_ID,
                                                   profile.env, Config.NOTIFY_SERVICE_API_KEY, profile.mobile,
                                                   expected_created_at)
    m = re.search('\d{5}', verify_code_message)
    if not m:
        pytest.fail("Could not find the verify code in notification body")
    return m.group(0)


@retry(RetryException, tries=15, delay=Config.EMAIL_DELAY)
def get_notification_via_api(service_id, template_id, env, api_key, sent_to, expected_created_at):
    client = NotificationsAPIClient(Config.NOTIFY_API_URL,
                                    service_id,
                                    api_key)
    resp = client.get('notifications?limit_days=1', params={'include_jobs': True})
    for notification in resp['notifications']:
        t_id = notification['template']['id']
        to = notification['to']
        created_at = datetime.strptime(notification['created_at'], "%Y-%m-%dT%H:%M:%S.%f+00:00")
        if t_id == template_id and to == sent_to and created_at > expected_created_at:
            return notification['body']
    else:
        message = 'Could not find notification with template {} to {}' \
            .format(template_id,
                    sent_to)
        raise RetryException(message)
