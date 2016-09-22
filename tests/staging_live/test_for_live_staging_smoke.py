from tests.utils import (
    create_temp_csv,
    get_notification_by_id_via_api,
    get_delivered_notification,
    assert_notification_body)

from tests.pages import UploadCsvPage

from notifications_python_client.notifications import NotificationsAPIClient


def test_for_live_staging_smoke(driver, base_url, profile, login_user):
    upload_csv_page = UploadCsvPage(driver)
    send_notification_via_csv(profile, upload_csv_page, 'sms')
    send_notification_via_csv(profile, upload_csv_page, 'email')
    upload_csv_page.sign_out()

    client = NotificationsAPIClient(profile.notify_api_url,
                                    profile.service_id,
                                    profile.api_key)

    send_sms_via_api(client, profile)
    send_email_via_api(client, profile)


def send_notification_via_csv(profile, upload_csv_page, message_type):
    if message_type == 'sms':
        template_id = profile.sms_template_id
        directory, filename = create_temp_csv(profile.mobile, 'phone number')
        to = profile.mobile
    elif message_type == 'email':
        template_id = profile.email_template_id
        directory, filename = create_temp_csv(profile.email, 'email address')
        to = profile.email

    upload_csv_page.go_to_upload_csv_for_service_and_template(profile.service_id,
                                                              template_id)
    upload_csv_page.upload_csv(directory, filename)
    notification_id = upload_csv_page.get_notification_id_after_upload()
    notification = get_notification_by_id_via_api(notification_id,
                                                  profile.service_id,
                                                  template_id,
                                                  profile.api_key,
                                                  to)

    assert notification["id"] == notification_id
    assert "The quick brown fox jumped over the lazy dog" in notification["body"]


def send_sms_via_api(client, profile):
    resp_json = client.send_sms_notification(profile.mobile, profile.sms_template_id)
    message, notification_id = _assert_notification_status(client, profile, resp_json)
    assert_notification_body(client, message, notification_id)


def send_email_via_api(client, profile):
    resp_json = client.send_email_notification(profile.email, profile.email_template_id)
    message, notification_id = _assert_notification_status(client, profile, resp_json)
    assert_notification_body(client, message, notification_id)


def _assert_notification_status(client, profile, resp_json):
    notification_id = resp_json['data']['notification']['id']
    expected_status = 'sending' if profile.env == 'dev' else 'delivered'
    message = get_delivered_notification(client, notification_id, expected_status)
    return message, notification_id


def assert_notification_body(client, message, notification_id):
    assert "The quick brown fox jumped over the lazy dog" in message
    resp_json = client.get_notification_by_id(notification_id)
    assert resp_json['data']['notification']['id'] == notification_id
