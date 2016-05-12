from requests import session

from config import Config

from tests.utils import (
    get_sms_via_heroku,
    get_email_body,
    remove_all_emails
)

from notifications_python_client.notifications import NotificationsAPIClient


def _create_client(service_id, api_key):
    client = NotificationsAPIClient(
        Config.NOTIFY_API_URL,
        service_id,
        api_key)
    return client


def test_python_client_sms(profile):
    service_id = profile['config'].SERVICE_ID
    api_key = profile['config'].API_KEY
    template_id = profile['config'].SMS_TEMPLATE_ID

    client = _create_client(service_id, api_key)
    resp_json = client.send_sms_notification(profile['mobile'], template_id)
    assert 'result' not in resp_json['data']
    notification_id = resp_json['data']['notification']['id']
    message = get_sms_via_heroku(session())
    assert "The quick brown fox jumped over the lazy dog" in message
    resp_json = client.get_notification_by_id(notification_id)
    assert resp_json['data']['notification']['status'] in ['sending', 'delivered']


def test_python_client_email(profile):

    remove_all_emails(email_folder=profile['config'].EMAIL_NOTIFICATION_LABEL)
    service_id = profile['config'].SERVICE_ID
    api_key = profile['config'].API_KEY
    template_id = profile['config'].EMAIL_TEMPLATE_ID

    client = _create_client(service_id, api_key)

    try:
        resp_json = client.send_email_notification(profile['email'], template_id)

        notification_id = resp_json['data']['notification']['id']
        message = get_email_body(
            profile['email'],
            profile['password'],
            profile['config'].EMAIL_NOTIFICATION_LABEL)
    finally:
        remove_all_emails(email_folder=profile['config'].EMAIL_NOTIFICATION_LABEL)
    assert "The quick brown fox jumped over the lazy dog" in message
    resp_json = client.get_notification_by_id(notification_id)
    assert resp_json['data']['notification']['status'] in ['sending', 'delivered']
