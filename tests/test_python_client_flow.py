from requests import session

from config import Config
from tests.utils import (
    get_sms_via_heroku,
    get_email_body,
    remove_all_emails
)

from tests.pages.rollups import get_service_templates_and_api_key_for_tests

from notifications_python_client.notifications import NotificationsAPIClient

test_ids_and_client = {}


def _create_client(service_id, api_key):
    client = NotificationsAPIClient(
        Config.NOTIFY_API_URL,
        service_id,
        api_key)
    return client


def get_test_ids_and_client(driver, test_profile):
    if not test_ids_and_client:
        test_ids = get_service_templates_and_api_key_for_tests(driver, test_profile)
        client = _create_client(test_ids['service_id'], test_ids['api_key'])
        test_ids_and_client['test_ids'] = test_ids
        test_ids_and_client['client'] = client
    return test_ids_and_client


def test_python_client_sms(driver, test_profile):

    test_controls = get_test_ids_and_client(driver, test_profile)
    client = test_controls['client']
    test_ids = test_controls['test_ids']

    resp_json = client.send_sms_notification(
        Config.TWILIO_TEST_NUMBER,
        test_ids['sms_template_id'])
    assert 'result' not in resp_json['data']
    notification_id = resp_json['data']['notification']['id']
    message = get_sms_via_heroku(session())
    assert "The quick brown fox jumped over the lazy dog" in message
    resp_json = client.get_notification_by_id(notification_id)
    assert resp_json['data']['notification']['status'] in ['sending', 'delivered']


def test_python_client_email(driver, test_profile):

    remove_all_emails(email_folder=Config.EMAIL_NOTIFICATION_LABEL)

    test_controls = get_test_ids_and_client(driver, test_profile)
    client = test_controls['client']
    test_ids = test_controls['test_ids']

    try:
        resp_json = client.send_email_notification(
            test_profile['email'],
            test_ids['email_template_id'])
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
    assert resp_json['data']['notification']['status'] in ['sending', 'delivered']
