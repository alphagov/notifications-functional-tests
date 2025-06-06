from retry.api import retry_call

from config import config
from tests.pages import UploadCsvPage
from tests.postman import (
    get_notification_by_id_via_api,
    send_notification_via_csv,
)
from tests.test_utils import (
    NotificationStatuses,
    assert_notification_body,
    recordtime,
)


@recordtime
def test_admin(driver, client_live_key, login_user):
    upload_csv_page = UploadCsvPage(driver)

    csv_sms_notification_id = send_notification_via_csv(upload_csv_page, "sms")
    csv_sms_notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[
            client_live_key,
            csv_sms_notification_id,
            NotificationStatuses.SENT,
        ],
        tries=config["smoke_test_csv_notification_retry_time"],
        delay=config["notification_retry_interval"],
    )
    assert_notification_body(csv_sms_notification_id, csv_sms_notification)

    csv_email_notification_id = send_notification_via_csv(upload_csv_page, "email")
    csv_email_notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[
            client_live_key,
            csv_email_notification_id,
            NotificationStatuses.SENT,
        ],
        tries=config["smoke_test_csv_notification_retry_time"],
        delay=config["notification_retry_interval"],
    )

    assert_notification_body(csv_email_notification_id, csv_email_notification)

    upload_csv_page.sign_out()
