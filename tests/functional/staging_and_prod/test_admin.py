import pytest

from retry.api import retry_call
from config import config

from tests.pages import UploadCsvPage

from tests.postman import (
    send_notification_via_csv,
    get_notification_by_id_via_api,
)

from tests.test_utils import assert_notification_body, recordtime, NotificationStatuses


@pytest.mark.skip(reason="intermittent pager duty alerts due to queue backlog")
def test_admin(driver, client, login_user):
    upload_csv_page = UploadCsvPage(driver)
    csv_sms_notification_id = send_notification_via_csv(upload_csv_page, 'sms')
    csv_sms_notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[client, csv_sms_notification_id, NotificationStatuses.SENT],
        tries=config['notification_retry_times'],
        delay=config['notification_retry_interval']
    )
    assert_notification_body(csv_sms_notification_id, csv_sms_notification)

    csv_email_notification_id = send_notification_via_csv(upload_csv_page, 'email')
    csv_email_notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[client, csv_email_notification_id, NotificationStatuses.SENT],
        tries=config['notification_retry_times'],
        delay=config['notification_retry_interval']
    )

    assert_notification_body(csv_email_notification_id, csv_email_notification)

    upload_csv_page.sign_out()
