from retry.api import retry_call
from config import Config

from tests.postman import (
    send_notification_via_api,
    get_notification_by_id_via_api
)

from tests.test_utils import assert_notification_body, recordtime


@recordtime
def test_send_sms_and_email_via_api(profile, client):
    notification_id = send_notification_via_api(client, profile.email_template_id, profile.email, 'email')

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[client, notification_id, ['sending', 'delivered']],
        tries=Config.NOTIFICATION_RETRY_TIMES,
        delay=Config.NOTIFICATION_RETRY_INTERVAL
    )
    assert_notification_body(notification_id, notification)
