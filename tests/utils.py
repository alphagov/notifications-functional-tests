import pytest
import csv
import imaplib
from time import sleep
from io import (StringIO, BytesIO)

from _pytest.runner import fail
from bs4 import BeautifulSoup
from config import Config


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


def find_csrf_token(html):
    soup = BeautifulSoup(html, 'html.parser')
    token = soup.find('input', {'name': 'csrf_token'}).get('value')
    return token


def find_page_title(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.title.text.strip()


def sign_in(client, base_url, email, pwd):
    try:
        get_sign_resp = client.get(base_url + '/sign-in')
        token = find_csrf_token(get_sign_resp.text)
        data = {'email_address': email,
                'password': pwd,
                'csrf_token': token}
        post_sign_in_resp = client.post(
            base_url + '/sign-in',
            data=data,
            headers=dict(Referer=base_url + '/sign-in'))
        get_two_factor = client.get(base_url + '/two-factor')
        next_token = find_csrf_token(get_two_factor.text)
        sms_code = get_sms_via_heroku(client)
        two_factor_data = {'sms_code': sms_code,
                           'csrf_token': next_token}
        post_two_factor = client.post(base_url + '/two-factor', data=two_factor_data,
                                      headers=dict(Referer=base_url + '/two-factor'))

    except:
        pytest.fail("Unable to log in")


def sign_out(client, base_url):
    try:
        get_logout = client.get(base_url + '/sign-out')
        assert get_logout.status_code == 200
    except:
        pytest.fail("Unable to log out")


def create_sample_csv_file(numbers):
    content = StringIO()
    retval = None
    with content as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["phone number"])
        csvwriter.writerows(numbers)
        retval = BytesIO(content.getvalue().encode('utf-8'))
    return retval


def get_sms_via_heroku(client):
    import json
    response = client.get('https://notify-sms-inbox.herokuapp.com/')
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
            response = client.get('https://notify-sms-inbox.herokuapp.com/')
            j = json.loads(response.text)

    try:
        return j['sms_code']
    except KeyError:
        fail('No sms code delivered')
