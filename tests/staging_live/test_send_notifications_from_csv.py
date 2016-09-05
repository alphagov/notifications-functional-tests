from tests.utils import (
    create_temp_csv,
    get_notification_via_api,
    get_delivered_notification)

from tests.pages import UploadCsvPage

from notifications_python_client.notifications import NotificationsAPIClient


def test_send_notifications_from_csv(driver, base_url, profile, login_user):
    upload_csv_page = UploadCsvPage(driver)

    email_via_csv(profile, upload_csv_page)
    sms_via_csv(profile, upload_csv_page)

    upload_csv_page.sign_out()

    client = NotificationsAPIClient(profile.notify_api_url,
                                    profile.service_id,
                                    profile.api_key)

    send_sms_via_api(client, profile)
    send_email_via_api(client, profile)


def sms_via_csv(profile, upload_csv_page):
    # go to upload csv for sms notification page
    upload_csv_page.go_to_upload_csv_for_service_and_template(profile.service_id,
                                                              profile.sms_template_id)
    # create csv file to use for sms notification
    directory, filename = create_temp_csv(profile.mobile, 'phone number')
    upload_csv_page.upload_csv(directory, filename)
    message = get_notification_via_api(profile.service_id, profile.sms_template_id,
                                       profile.env, profile.api_key, profile.mobile)
    assert "The quick brown fox jumped over the lazy dog" in message


def email_via_csv(profile, upload_csv_page):
    upload_csv_page.go_to_upload_csv_for_service_and_template(profile.service_id,
                                                              profile.email_template_id)
    # create csv file to use for email notification
    directory, filename = create_temp_csv(profile.email, 'email address')
    upload_csv_page.upload_csv(directory, filename)
    email_body = get_notification_via_api(profile.service_id, profile.email_template_id,
                                          profile.env, profile.api_key, profile.email)
    assert "The quick brown fox jumped over the lazy dog" in email_body


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
