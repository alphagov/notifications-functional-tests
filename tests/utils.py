import pytest
import csv
import email as email_lib
import imaplib
import json
import re
from time import sleep
from retry import retry
from _pytest.runner import fail

from notifications_python_client.notifications import NotificationsAPIClient
from notifications_python_client.errors import HTTPError
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


def get_sms_via_heroku(client, environment=None):
    if environment is None:
        environment = Config.ENVIRONMENT
    url = 'https://notify-sms-inbox.herokuapp.com/' + environment
    response = client.get(url)
    j = json.loads(response.text)
    x = 0
    loop_condition = True
    while loop_condition:
        if response.status_code == 200:
            loop_condition = False
        if x > 12:
            loop_condition = False
        if j['result'] == 'error':
            sleep(5)
            x += 1
            response = client.get(url)
            j = json.loads(response.text)

    try:
        return j['sms_code']
    except KeyError:
        fail('No sms code delivered')


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


@retry(RetryException, tries=Config.EMAIL_TRIES, delay=Config.EMAIL_DELAY)
def get_delivered_notification(client, notification_id):
    """
    Waits until a notification is delivered, and then returns its response json.

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
    if status in ('created', 'sending'):
        raise RetryException('Notification still sending')
    assert status == 'delivered'
    return resp_json


def generate_unique_email(email, uuid):
    parts = email.split('@')
    return "{}+{}@{}".format(parts[0], uuid, parts[1])


def get_link(profile, email_label):
    import re
    try:
        email_body = get_email_body(profile, email_label)
        match = re.search('http[s]?://\S+', email_body, re.MULTILINE)
        if match:
            return match.group(0)
        else:
            pytest.fail("Couldn't get the registraion link from the email")
    finally:
        remove_all_emails(email_folder=email_label)


def get_verify_code():
    from requests import session
    verify_code = get_sms_via_heroku(session())
    if not verify_code:
        pytest.fail("Could not get the verify code")
    m = re.search('\d{5}', verify_code)
    if not m:
        pytest.fail("Could not get the verify code")
    return m.group(0)


@retry(RetryException, tries=15, delay=2)
def do_verify(driver, profile):
    verify_code = get_verify_code_from_api(profile)
    verify_page = VerifyPage(driver)
    verify_page.verify(verify_code)
    if verify_page.has_code_error():
        raise RetryException


def get_verify_code_from_api(profile):
    client = NotificationsAPIClient(Config.NOTIFY_API_URL,
                                    Config.NOTIFY_SERVICE_ID,
                                    Config.NOTIFY_SERVICE_API_KEY)
    resp = client.get('notifications')
    verify_code_message = _get_latest_verify_code_message(resp, profile)
    m = re.search('\d{5}', verify_code_message)
    if not m:
        pytest.fail("Could not find the verify code in notification body")
    return m.group(0)


def _get_latest_verify_code_message(resp, profile):
    for notification in resp['notifications']:
        if notification['to'] == profile.mobile and notification['template']['name'] == 'Notify SMS verify code':
            return notification['body']
    raise RetryException


@retry(RetryException, tries=15, delay=2)
def get_sms_via_api(service_id, template_id, profile, api_key):
    client = NotificationsAPIClient(Config.NOTIFY_API_URL,
                                    service_id,
                                    api_key)
    if profile.env == 'dev':
        expected_status = 'sending'
    else:
        expected_status = 'delivered'
    resp = client.get('notifications')
    for notification in resp['notifications']:
        t_id = notification['template']['id']
        to = notification['to']
        status = notification['status']
        if t_id == template_id and to == profile.mobile and status == expected_status:
            return notification['body']
    else:
        message = 'Could not find notification with template {} to number {} with a status of {}' \
            .format(template_id,
                    profile.mobile,
                    expected_status)
        raise RetryException(message)


def get_email_message(profile, email_label):
    try:
        return get_email_body(profile, email_label)
    finally:
        remove_all_emails(email_folder=email_label)


def send_to_deskpro(config, message):
    import os
    import requests
    email = os.environ.get('live_DESKPRO_PERSON_EMAIL')
    deskpro_department_id = os.environ.get('live_DESKPRO_DEPT_ID')
    deskpro_api_key = os.environ.get('live_DESKPRO_API_KEY')
    deskpro_api_host = os.environ.get('live_DESKPRO_API_HOST')
    deskpro_agent_team_id = os.environ.get('live_DESKPRO_ASSIGNED_AGENT_TEAM_ID')

    message = message

    data = {'person_email': email,
            'department_id': deskpro_department_id,
            'subject': 'Notify incident report',
            'message': message,
            'agent_team_id': deskpro_agent_team_id
            }
    headers = {
        "X-DeskPRO-API-Key": deskpro_api_key,
        'Content-Type': "application/x-www-form-urlencoded"
    }

    resp = requests.post(
        deskpro_api_host + '/api/tickets',
        data=data,
        headers=headers)

    if resp.status_code != 201:
        print("Deskpro create ticket request failed with {} '{}'".format(resp.status_code, resp.json()))
