from notifications_python_client.errors import HTTPError

from config import config
from tests.test_utils import RetryException, create_temp_csv


def send_notification_via_api(client, template_id, to, message_type):
    personalisation = {"build_id": "No build id"}

    if message_type == "sms":
        resp_json = client.send_sms_notification(to, template_id, personalisation)
    elif message_type == "email":
        resp_json = client.send_email_notification(to, template_id, personalisation)
    elif message_type == "letter":
        to.update(personalisation)
        resp_json = client.send_letter_notification(template_id, to)

    return resp_json["id"]


def send_precompiled_letter_via_api(reference, client, pdf_file):
    resp_json = client.send_precompiled_letter_notification(reference, pdf_file)
    return resp_json["id"]


def send_notification_via_csv(upload_csv_page, message_type, seeded=False):
    service_id = config["service"]["id"] if seeded else config["service"]["id"]
    email = (
        config["service"]["seeded_user"]["email"] if seeded else config["user"]["email"]
    )
    letter_contact = config["letter_contact_data"]

    if message_type == "sms":
        template_id = config["service"]["templates"]["sms"]
        directory, filename = create_temp_csv(
            {"phone number": config["user"]["mobile"]}
        )
    elif message_type == "email":
        template_id = config["service"]["templates"]["email"]
        directory, filename = create_temp_csv({"email address": email})
    elif message_type == "letter":
        template_id = config["service"]["templates"]["letter"]
        directory, filename = create_temp_csv(letter_contact)

    upload_csv_page.go_to_upload_csv_for_service_and_template(service_id, template_id)
    upload_csv_page.upload_csv(directory, filename)
    notification_id = upload_csv_page.get_notification_id_after_upload()

    return notification_id


def get_notification_by_id_via_api(client, notification_id, expected_statuses):
    if isinstance(expected_statuses, str):
        expected_statuses = {expected_statuses}
    try:
        resp = client.get_notification_by_id(notification_id)
        notification_status = resp["status"]
        if notification_status not in expected_statuses:
            raise RetryException(
                (
                    "Notification in wrong status "
                    "id: {id} "
                    "status: {status} "
                    "created_at: {created_at} "
                    "sent_at: {sent_at} "
                    "completed_at: {completed_at}"
                ).format(**resp)
            )
        return resp
    except HTTPError as e:
        if e.status_code == 404:
            message = "Notification not created yet for id: {}".format(notification_id)
            raise RetryException(message)
        else:
            raise


def get_pdf_for_letter_via_api(client, notification_id):
    return client.get_pdf_for_letter(notification_id)
