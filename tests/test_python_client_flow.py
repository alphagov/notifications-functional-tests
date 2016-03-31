from requests import session

from config import Config
from tests.utils import (
    get_sms_via_heroku,
    get_email_body,
    remove_all_emails)
from notifications_python_client.notifications import NotificationsAPIClient


def _create_client():
    client = NotificationsAPIClient(
        Config.NOTIFY_API_URL,
        Config.FUNCTIONAL_SERVICE_ID,
        Config.FUNCTIONAL_API_KEY)
    return client


def test_python_client_sms():
    client = _create_client()
    resp_json = client.send_sms_notification(
        Config.TWILIO_TEST_NUMBER,
        Config.FUNCTIONAL_SMS_TEMPLATE_ID)
    assert 'result' not in resp_json['data']
    notification_id = resp_json['data']['notification']['id']
    message = get_sms_via_heroku(session())
    assert "The quick brown fox jumped over the lazy dog" in message
    resp_json = client.get_notification_by_id(notification_id)
    assert resp_json['data']['notification']['status'] in ['sent', 'delivered']


def test_python_client_email():
    remove_all_emails(email_folder=Config.EMAIL_NOTIFICATION_LABEL)
    client = _create_client()
    try:
        resp_json = client.send_email_notification(
            Config.FUNCTIONAL_TEST_EMAIL,
            Config.FUNCTIONAL_EMAIL_TEMPLATE_ID)
        assert 'result' not in resp_json['data']
        notification_id = resp_json['data']['notification']['id']
        message = get_email_body(
            Config.FUNCTIONAL_TEST_EMAIL,
            Config.FUNCTIONAL_TEST_PASSWORD,
            Config.EMAIL_NOTIFICATION_LABEL)
    finally:
        remove_all_emails(email_folder=Config.EMAIL_NOTIFICATION_LABEL)
    assert "The quick brown fox jumped over the lazy dog" in message
    resp_json = client.get_notification_by_id(notification_id)
    assert resp_json['data']['notification']['status'] in ['sent', 'delivered']
