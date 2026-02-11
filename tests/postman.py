from notifications_python_client.errors import HTTPError
import uuid
from config import config
from tests.pages import JobPage, SendViaCsvPreviewPage
from tests.test_utils import RetryException, get_temp_csv_for_message_type


def send_notification_via_api(client, template_id, to, message_type):
    personalisation = {"build_id": f"{uuid.uuid4()}"}

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


def send_notification_via_csv(send_via_csv_page, message_type: str, seeded: bool = False):
    template_id = config["service"]["templates"][message_type]
    _, directory, filename = get_temp_csv_for_message_type(message_type, seeded=seeded, include_build_id=True)

    send_via_csv_page.go_to_upload_csv_for_service_and_template(config["service"]["id"], template_id)
    send_via_csv_page.upload_csv(directory, filename)

    send_via_csv_preview_page = SendViaCsvPreviewPage(send_via_csv_page.driver)
    send_via_csv_preview_page.click_send()

    job_page = JobPage(send_via_csv_preview_page.driver)
    job_page.wait_until_current(time=20)

    return job_page


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
            message = f"Notification not created yet for id: {notification_id}"
            raise RetryException(message) from e
        else:
            raise


def get_pdf_for_letter_via_api(client, notification_id):
    return client.get_pdf_for_letter(notification_id)
