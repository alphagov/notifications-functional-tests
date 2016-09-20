import pytest

from tests.utils import assert_notification_body, get_delivered_notification


@pytest.mark.parametrize("message_type, billable_units", [('sms', 1), ('email', 0)])
def test_send_sms_and_email_via_api(driver, profile, client, message_type, billable_units):
    notification_id = send_message_via_api(message_type, client, profile)
    message = get_delivered_notification(client, notification_id, 'delivered')
    assert_notification_body(client, message, notification_id)
    assert message["billable_units"] == billable_units


def send_message_via_api(message_type, client, profile):
    if message_type == 'sms':
        resp_json = client.send_sms_notification(profile.mobile, profile.sms_template_id)
    elif message_type == 'email':
        resp_json = client.send_email_notification(profile.email, profile.email_template_id)

    return resp_json['data']['notification']['id']
