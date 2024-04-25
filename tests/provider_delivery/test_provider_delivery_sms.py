from retry.api import retry_call

from config import config
from tests.postman import (
    get_notification_by_id_via_api,
    send_notification_via_api,
)
from tests.test_utils import NotificationStatuses, assert_notification_body


def test_provider_sms_delivery_via_api(client_live_key):
    notification_id = send_notification_via_api(
        client_live_key,
        config["service"]["templates"]["sms"],
        # we can't reliably use the user test number, as this is set to a TV number. TV numbers often don't reliably
        # report delivery. Instead, if we send to the inbound provider test number, that returns a delivery receipt
        # promptly so we check for that instead.
        config["service"]["inbound_number"],
        "sms",
    )

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[
            client_live_key,
            notification_id,
            NotificationStatuses.DELIVERED,
        ],
        tries=config["provider_retry_times"],
        delay=config["provider_retry_interval"],
    )
    assert_notification_body(notification_id, notification)
