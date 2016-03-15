import uuid
import datetime
import sys
import re
import time
import imaplib
import email as email_lib
import email.header
import pytest
from requests import session
from config import Config
from tests.utils import (retrieve_sms_with_wait,
                         delete_sms_message,
                         find_csrf_token,
                         get_sms,
                         create_sample_csv_file,
                         sign_in,
                         sign_out,
                         delete_default_sms)


def test_csv_upload_journey():
    delete_default_sms()
    client = session()
    base_url = Config.NOTIFY_ADMIN_URL
    try:
        sign_in(
            client,
            base_url,
            Config.FUNCTIONAL_TEST_EMAIL,
            Config.FUNCTIONAL_TEST_PASSWORD)
        csv_upload_url = '{}/services/{}/send/{}'.format(
            base_url,
            Config.FUNCTIONAL_SERVICE_ID,
            Config.FUNCTIONAL_TEMPLATE_ID)
        get_csv_upload = client.get(csv_upload_url)
        next_token = find_csrf_token(get_csv_upload.text)
        csv_file = create_sample_csv_file([[Config.TWILIO_TEST_NUMBER]])
        files = {'file': ("preview_file.csv", csv_file, 'text/csv')}
        data = {'csrf_token': next_token}
        msgs = []
        post_csv_upload = client.post(
            csv_upload_url,
            data=data,
            files=files,
            headers=dict(Referer=csv_upload_url))
        assert post_csv_upload.status_code == 200
        assert 'services/{}/check'.format(Config.FUNCTIONAL_SERVICE_ID) in post_csv_upload.url
        next_token = find_csrf_token(post_csv_upload.text)
        data = data = {'csrf_token': next_token}
        post_check_sms = client.post(
            post_csv_upload.url,
            data=data,
            headers=dict(Referer=post_csv_upload.url))
        assert post_check_sms.status_code == 200
        assert '/jobs' in post_check_sms.url
        msgs = retrieve_sms_with_wait(Config.FUNCTIONAL_TEST_EMAIL)
    finally:
        # Make sure to delete all msgs from the account
        delete_default_sms()
    # Test will fail if there is not 1 message (we expect only 1 message)
    assert len(msgs) == 1, 'Expecting to retrieve 1 sms message in functional test for user: {}'.format(
        Config.FUNCTIONAL_TEST_EMAIL)
    # Verify the correct sms message was sent
    assert "The quick brown fox jumped over the lazy dog" in msgs[0].body
    sign_out(client, base_url)
