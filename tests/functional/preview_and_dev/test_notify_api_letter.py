from io import BytesIO
import base64
from retry.api import retry_call
from config import Config

from tests.postman import (
    get_notification_by_id_via_api,
    send_notification_via_api,
    send_precompiled_letter_via_api,
    NotificationStatuses
)

from tests.functional.preview_and_dev.pdf_consts import one_page_pdf
from tests.test_utils import assert_client_reference, assert_notification_body, recordtime


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


@recordtime
def test_send_precompiled_letter_notification_via_api(profile, seeded_client_using_test_key):
    notification_id = send_precompiled_letter_via_api(
        profile,
        seeded_client_using_test_key,
        BytesIO(base64.b64decode(one_page_pdf))
    )

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[seeded_client_using_test_key, notification_id, NotificationStatuses.PENDING_VIRUS_CHECK],
        tries=Config.NOTIFICATION_RETRY_TIMES,
        delay=Config.NOTIFICATION_RETRY_INTERVAL
    )
    assert_client_reference(profile, notification['reference'])
