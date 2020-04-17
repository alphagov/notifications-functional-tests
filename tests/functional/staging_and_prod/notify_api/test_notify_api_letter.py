from io import BytesIO
import base64

from retry.api import retry_call
from config import config

from tests.postman import (
    send_precompiled_letter_via_api,
    get_notification_by_id_via_api,
)
from tests.test_utils import recordtime, NotificationStatuses
from tests.functional.preview_and_dev.consts import correct_letter


@recordtime
def test_send_precompiled_letter_notification_via_api(seeded_client_using_test_key):

    reference = config['name'].replace(" ", "_") + "_delivered"

    notification_id = send_precompiled_letter_via_api(
        reference,
        seeded_client_using_test_key,
        BytesIO(base64.b64decode(correct_letter))
    )

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[seeded_client_using_test_key, notification_id, NotificationStatuses.RECEIVED],
        tries=config['notification_retry_times'],
        delay=config['notification_retry_interval']
    )

    assert reference == notification['reference']
