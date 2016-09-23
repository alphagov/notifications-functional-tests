import pytest

from tests.pages import UploadCsvPage

from tests.postman import (
    send_notification_via_api,
    send_notification_via_csv,
    get_notification_by_id_via_api
)

from tests.utils import assert_notification_body


def test_for_live_staging_smoke(driver, base_url, client, profile, login_user):
    upload_csv_page = UploadCsvPage(driver)
    csv_sms_notification_id = send_notification_via_csv(profile, upload_csv_page, 'sms')
    csv_sms_notification = get_notification_by_id_via_api(client, csv_sms_notification_id, ['sending', 'delivered'])
    assert_notification_body(csv_sms_notification_id, csv_sms_notification)

    csv_email_notification_id = send_notification_via_csv(profile, upload_csv_page, 'email')
    csv_email_notification = get_notification_by_id_via_api(client, csv_email_notification_id, ['sending', 'delivered'])
    assert_notification_body(csv_email_notification_id, csv_email_notification)

    upload_csv_page.sign_out()


@pytest.mark.parametrize('message_type, expected_statuses', [
    ('sms', ['sending', 'delivered']),
    ('email', ['sending', 'delivered'])
])
def test_send_sms_and_email_via_api(profile, client, message_type, expected_statuses):
    template_id = profile.sms_template_id if message_type == 'sms' else profile.email_template_id
    to = profile.mobile if message_type == 'sms' else profile.email
    notification_id = send_notification_via_api(client, template_id, to, message_type)
    notification = get_notification_by_id_via_api(client, notification_id, expected_statuses)
    assert_notification_body(notification_id, notification)
