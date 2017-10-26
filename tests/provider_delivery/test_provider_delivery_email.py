from retry.api import retry_call
from config import Config
from tests.postman import (
    send_notification_via_api,
    get_notification_by_id_via_api
)

from tests.test_utils import assert_notification_body


def test_provider_email_delivery_via_api(profile, client):
    notification_id = send_notification_via_api(
        client, profile.jenkins_build_email_template_id,
        profile.email, 'email'
    )
    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[client, notification_id, 'delivered'],
        tries=Config.PROVIDER_RETRY_TIMES,
        delay=Config.PROVIDER_RETRY_INTERVAL
    )
    assert_notification_body(notification_id, notification)
