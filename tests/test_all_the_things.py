from tests.postman import (
    send_notification_via_csv,
    get_notification_by_id_via_api)

from tests.utils import (
    get_email_body,
    remove_all_emails,
    do_user_registration,
    do_user_can_invite_someone_to_notify,
    do_edit_and_delete_email_template,
    assert_notification_body
    )

from tests.pages import UploadCsvPage

from tests.pages.rollups import get_service_templates_and_api_key_for_tests

from notifications_python_client.notifications import NotificationsAPIClient


def _get_email_message(profile):
    try:
        return get_email_body(profile, profile.email_notification_label)

    finally:
        remove_all_emails(email_folder=profile.email_notification_label)


def test_everything(driver, profile, base_url, base_api_url):
    do_user_registration(driver, profile, base_url)
    test_ids = get_service_templates_and_api_key_for_tests(driver, profile)

    client = NotificationsAPIClient(base_api_url, test_ids['service_id'], test_ids['api_key'])

    upload_csv_page = UploadCsvPage(driver)

    email_notification_id = send_notification_via_csv(profile, upload_csv_page, 'email')
    email_notification = get_notification_by_id_via_api(
        client,
        email_notification_id,
        ['sending', 'delivered']
    )
    assert_notification_body(email_notification_id, email_notification)

    sms_notification_id = send_notification_via_csv(profile, upload_csv_page, 'sms')
    sms_notification = get_notification_by_id_via_api(
        client,
        sms_notification_id,
        ['sending', 'delivered']
    )
    assert_notification_body(sms_notification_id, sms_notification)

    do_edit_and_delete_email_template(driver, profile)
    do_user_can_invite_someone_to_notify(driver, profile, base_url)
