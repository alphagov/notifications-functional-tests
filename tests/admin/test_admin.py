from tests.pages import UploadCsvPage

from tests.postman import (
    send_notification_via_csv,
    get_notification_by_id_via_api
)

from tests.utils import assert_notification_body


def test_admin(driver, base_url, client, profile, login_user):
    upload_csv_page = UploadCsvPage(driver)
    csv_sms_notification_id = send_notification_via_csv(profile, upload_csv_page, 'sms')
    csv_sms_notification = get_notification_by_id_via_api(client, csv_sms_notification_id, ['sending', 'delivered'])
    assert_notification_body(csv_sms_notification_id, csv_sms_notification)

    csv_email_notification_id = send_notification_via_csv(profile, upload_csv_page, 'email')
    csv_email_notification = get_notification_by_id_via_api(client, csv_email_notification_id, ['sending', 'delivered'])
    assert_notification_body(csv_email_notification_id, csv_email_notification)

    upload_csv_page.sign_out()
