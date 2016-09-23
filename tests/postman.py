from retry import retry
from config import Config
from tests.utils import create_temp_csv, RetryException
from notifications_python_client.errors import HTTPError


class RetryException(Exception):
    pass


def send_notification_via_api(client, template_id, to, message_type):
    if message_type == 'sms':
        # resp_json = client.send_sms_notification(profile.mobile, profile.sms_template_id)
        resp_json = client.send_sms_notification(to, template_id)
    elif message_type == 'email':
        # resp_json = client.send_email_notification(profile.email, profile.email_template_id)
        resp_json = client.send_email_notification(to, template_id)

    return resp_json['data']['notification']['id']


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

    return notification_id


@retry(RetryException, tries=15, delay=Config.EMAIL_DELAY)
def get_notification_by_id_via_api(client, notification_id, expected_statuses):
    try:
        resp = client.get_notification_by_id(notification_id)
        notification_status = resp['data']['notification']['status']
        if notification_status not in expected_statuses:
            raise RetryException('Notification still in {}'.format(notification_status))
        return resp["data"]["notification"]
    except HTTPError as e:
        if e.status_code == 404:
            message = 'Notification not created yet for id: {}'.format(notification_id)
            raise RetryException(message)
        else:
            raise
