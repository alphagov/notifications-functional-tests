import pytest
import csv
import imaplib
import email as email_lib
from operator import attrgetter
from time import sleep
from io import (StringIO, BytesIO)
from bs4 import BeautifulSoup
from config import Config
from twilio.rest import TwilioRestClient


def retrieve_sms_with_wait(user_name):
    x = 0
    msgs = get_sms()
    loop_condition = True
    while loop_condition:
        if len(msgs) != 0:
            loop_condition = False
            break
        if x > 12:
            loop_condition = False
            break
        x += 1
        sleep(5)
        msgs = get_sms()

    return sorted(msgs, key=attrgetter('date_created'), reverse=True)


def get_sms():
    client = TwilioRestClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    messages = client.messages.list(to=Config.TWILIO_TEST_NUMBER)
    msgs = []
    if len(messages) > 0:
        msgs = [m for m in messages if m.direction == 'inbound']
    return msgs


def remove_all_emails(email, pwd, email_folder):
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


def delete_sms_messge(sid):
    from twilio.rest import TwilioRestClient

    client = TwilioRestClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    client.messages.delete(sid)


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
            headers=dict(Referer=base_url+'/sign-in'))
        get_two_factor = client.get(base_url + '/two-factor')
        next_token = find_csrf_token(get_two_factor.text)
        messages = retrieve_sms_with_wait(email)
        m = messages[0]
        two_factor_data = {'sms_code': m.body,
                           'csrf_token': next_token}
        post_two_factor = client.post(base_url + '/two-factor', data=two_factor_data,
                                      headers=dict(Referer=base_url+'/two-factor'))
        delete_sms_messge(m.sid)
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
