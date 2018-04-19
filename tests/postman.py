import os

from tests.test_utils import create_temp_csv, RetryException
from notifications_python_client.errors import HTTPError


def send_notification_via_api(client, template_id, to, message_type):
    jenkins_build_id = os.getenv('BUILD_ID', 'No build id')
    personalisation = {'build_id': jenkins_build_id}

    if message_type == 'sms':
        resp_json = client.send_sms_notification(to, template_id, personalisation)
    elif message_type == 'email':
        resp_json = client.send_email_notification(to, template_id, personalisation)
    elif message_type == 'letter':
        to.update(personalisation)
        resp_json = client.send_letter_notification(template_id, to)

    return resp_json['id']


def send_precompiled_letter_via_api(profile, client, pdf_file):
    resp_json = client.send_precompiled_letter_notification(profile.name, pdf_file)
    return resp_json['id']


def send_notification_via_csv(profile, upload_csv_page, message_type, seeded=False):
    service_id = profile.notify_research_service_id if seeded else profile.service_id
    email = profile.notify_research_service_email if seeded else profile.email
    letter_contact = profile.notify_research_letter_contact if seeded else None

    if message_type == 'sms':
        template_id = profile.jenkins_build_sms_template_id
        directory, filename = create_temp_csv({'phone number': profile.mobile})
    elif message_type == 'email':
        template_id = profile.jenkins_build_email_template_id
        directory, filename = create_temp_csv({'email address': email})
    elif message_type == 'letter':
        template_id = profile.jenkins_build_letter_template_id
        directory, filename = create_temp_csv(letter_contact)

    upload_csv_page.go_to_upload_csv_for_service_and_template(service_id, template_id)
    upload_csv_page.upload_csv(directory, filename)
    notification_id = upload_csv_page.get_notification_id_after_upload()

    return notification_id


class NotificationStatuses:
    PENDING_VIRUS_CHECK = 'pending-virus-check'
    RECEIVED = {'received'}
    DELIVERED = {'delivered', 'temporary-failure', 'permanent-failure'}
    SENT = RECEIVED | DELIVERED | {'sending'}


def get_notification_by_id_via_api(client, notification_id, expected_statuses):
    try:
        resp = client.get_notification_by_id(notification_id)
        notification_status = resp['status']
        if notification_status not in expected_statuses:
            raise RetryException(
                (
                    'Notification in wrong status '
                    'id: {id} '
                    'status: {status} '
                    'created_at: {created_at} '
                    'sent_at: {sent_at} '
                    'completed_at: {completed_at}'
                ).format(**resp)
            )
        return resp
    except HTTPError as e:
        if e.status_code == 404:
            message = 'Notification not created yet for id: {}'.format(notification_id)
            raise RetryException(message)
        else:
            raise
