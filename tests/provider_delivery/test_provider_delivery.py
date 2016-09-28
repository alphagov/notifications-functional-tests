import pytest

from tests.postman import (
    send_notification_via_api,
    get_notification_by_id_via_api
)

from tests.utils import assert_notification_body


@pytest.mark.parametrize("message_type, billable_units", [('sms', 1), ('email', 0)])
def test_send_sms_and_email_via_api(driver, profile, client, message_type, billable_units):
    template_id = profile.sms_template_id if message_type == 'sms' else profile.email_template_id
    to = profile.mobile if message_type == 'sms' else profile.email
    notification_id = send_notification_via_api(client, template_id, to, message_type)
    notification = get_notification_by_id_via_api(client, notification_id, ['delivered'])
    assert_notification_body(notification_id, notification)
    assert notification["billable_units"] == billable_units
