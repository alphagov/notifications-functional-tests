from retry.api import retry_call

from config import config
from tests.postman import (
    get_notification_by_id_via_api,
    send_notification_via_api,
)
from tests.test_utils import (
    NotificationStatuses,
    assert_notification_body,
    recordtime,
)


@recordtime
def test_send_sms_notification_via_api(client_test_key):
    notification_id = send_notification_via_api(
        client_test_key,
        config["service"]["templates"]["sms"],
        config["user"]["mobile"],
        "sms",
    )

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[client_test_key, notification_id, NotificationStatuses.SENT],
        tries=config["notification_retry_times"],
        delay=config["notification_retry_interval"],
    )
    assert_notification_body(notification_id, notification)
