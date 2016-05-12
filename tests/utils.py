import pytest
import csv
import email as email_lib
import imaplib
import json
from time import sleep
from retry import retry
from _pytest.runner import fail

from config import Config


class RetryException(Exception):
    pass


def remove_all_emails(email=None, pwd=None, email_folder=None):
    if not email:
        email = Config.FUNCTIONAL_TEST_EMAIL
    if not pwd:
        pwd = Config.FUNCTIONAL_TEST_PASSWORD
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
def get_email_body(email, pwd, email_folder):
    gimap = None
    try:
        gimap = imaplib.IMAP4_SSL('imap.gmail.com')
        try:
            rv, data = gimap.login(email, pwd)
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


def generate_unique_email(email, uuid):
    parts = email.split('@')
    return "{}+{}@{}".format(parts[0], uuid, parts[1])


def get_link(email, password, email_label):

    import re
    try:
        email_body = get_email_body(email, password, email_label)
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
    return verify_code[0:5]


def get_email_message(config):
    try:
        return get_email_body(config.FUNCTIONAL_TEST_EMAIL,
                              config.FUNCTIONAL_TEST_PASSWORD,
                              config.EMAIL_NOTIFICATION_LABEL)
    except:
        pytest.fail("Couldn't get notification email")
    finally:
        remove_all_emails(email_folder=config.EMAIL_NOTIFICATION_LABEL)


def send_to_deskpro(config, message):
    import os
    import requests
    email = os.environ.get('live_DESKPRO_PERSON_EMAIL')
    deskpro_team_id = os.environ.get('live_DESKPRO_TEAM_ID')
    deskpro_api_key = os.environ.get('live_DESKPRO_API_KEY')
    deskpro_api_host = os.environ.get('live_DESKPRO_API_HOST')
    message = message

    data = {'person_email': email,
            'department_id': deskpro_team_id,
            'subject': 'Notify incident report',
            'message': message
            }
    headers = {
        "X-DeskPRO-API-Key": deskpro_api_key,
        'Content-Type': "application/x-www-form-urlencoded"
    }
    import pdb
    pdb.set_trace()

    resp = requests.post(
        deskpro_api_host + '/api/tickets',
        data=data,
        headers=headers)

    if resp.status_code != 201:
        print("Deskpro create ticket request failed with {} '{}'".format(resp.status_code, resp.json()))
