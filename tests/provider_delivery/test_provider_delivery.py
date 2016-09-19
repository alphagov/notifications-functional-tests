from notifications_python_client import NotificationsAPIClient

from tests.utils import get_delivered_notification


def test_provider_delivery(profile):
    # sms message is delivered within 3 minutes
    # email message is delivered within 3 minutes

    client = NotificationsAPIClient(profile.notify_api_url,
                                    profile.service_id,
                                    profile.api_key)

    # send_sms_via_api(client, profile)
    send_email_via_api(client, profile)


def send_sms_via_api(client, profile):
    resp_json = client.send_sms_notification(profile.mobile, profile.sms_template_id)
    message, notification_id = _assert_notification_status(client, profile, resp_json)
    assert_notification_body(client, message, notification_id)


def send_email_via_api(client, profile):
    print('sending email')
    resp_json = client.send_email_notification(profile.email, profile.email_template_id)
    message, notification_id = _assert_notification_status(client, profile, resp_json)
    assert_notification_body(client, message, notification_id)


def _assert_notification_status(client, profile, resp_json):
    notification_id = resp_json['data']['notification']['id']
    expected_status = 'delivered'
    message = get_delivered_notification(client, notification_id, expected_status)
    return message, notification_id


def assert_notification_body(client, message, notification_id):
    assert "The quick brown fox jumped over the lazy dog" in message
    resp_json = client.get_notification_by_id(notification_id)
    assert resp_json['data']['notification']['id'] == notification_id
