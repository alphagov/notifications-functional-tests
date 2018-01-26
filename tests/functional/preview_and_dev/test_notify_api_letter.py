from retry.api import retry_call
from config import Config

from tests.postman import (
    send_notification_via_api,
    get_notification_by_id_via_api,
    NotificationStatuses
)

from tests.test_utils import assert_notification_body, recordtime


@recordtime
def test_send_letter_notification_via_api(profile, seeded_client_using_test_key):
    notification_id = send_notification_via_api(
        seeded_client_using_test_key, profile.jenkins_build_letter_template_id,
        profile.notify_research_letter_contact, 'letter'
    )

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[seeded_client_using_test_key, notification_id, NotificationStatuses.RECEIVED],
        tries=Config.NOTIFICATION_RETRY_TIMES,
        delay=Config.NOTIFICATION_RETRY_INTERVAL
    )
    assert_notification_body(notification_id, notification)
