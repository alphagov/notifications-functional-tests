from retry.api import retry_call
from config import config

from tests.postman import (
    send_notification_via_api,
    get_notification_by_id_via_api,
)

from tests.test_utils import assert_notification_body, recordtime, NotificationStatuses


@recordtime
def test_send_email_notification_via_api(client):
    notification_id = send_notification_via_api(
        client, config['service']['templates']['email'],
        config['user']['email'], 'email',
    )

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[client, notification_id, NotificationStatuses.SENT],
        tries=config['notification_retry_times'],
        delay=config['notification_retry_interval']
    )
    assert_notification_body(notification_id, notification)
