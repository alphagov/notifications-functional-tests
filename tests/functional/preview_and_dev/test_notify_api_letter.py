import base64
from io import BytesIO

import pytest
from retry.api import retry_call

from config import config
from tests.functional.preview_and_dev.consts import (
    correct_letter,
    pdf_with_virus,
)
from tests.postman import (
    get_notification_by_id_via_api,
    send_notification_via_api,
    send_precompiled_letter_via_api,
)
from tests.test_utils import (
    NotificationStatuses,
    assert_notification_body,
    recordtime,
)


@recordtime
@pytest.mark.xdist_group(name="api-client")
def test_send_letter_notification_via_api(seeded_client_using_test_key):
    notification_id = send_notification_via_api(
        seeded_client_using_test_key,
        config['service']['templates']['letter'],
        config['letter_contact_data'],
        'letter'
    )

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[seeded_client_using_test_key, notification_id, NotificationStatuses.RECEIVED],
        tries=config['notification_retry_times'],
        delay=config['notification_retry_interval']
    )
    assert_notification_body(notification_id, notification)


@recordtime
@pytest.mark.xdist_group(name="api-letters")
@pytest.mark.antivirus
def test_send_precompiled_letter_notification_via_api(seeded_client_using_test_key):

    reference = config['service_name'].replace(" ", "_") + "_delivered"

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


@recordtime
@pytest.mark.xdist_group(name="api-letters")
@pytest.mark.antivirus
def test_send_precompiled_letter_with_virus_notification_via_api(seeded_client_using_test_key):

    # This uses a file which drops the Eicar test virus into the temp directory
    # The dropper code _should_ be detected before the eicar virus

    reference = config['service_name'].replace(" ", "_") + "_virus_scan_failed"

    notification_id = send_precompiled_letter_via_api(
        reference,
        seeded_client_using_test_key,
        BytesIO(base64.b64decode(pdf_with_virus))
    )

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[seeded_client_using_test_key, notification_id, NotificationStatuses.VIRUS_SCAN_FAILED],
        tries=config['notification_retry_times'],
        delay=config['notification_retry_interval']
    )

    assert reference == notification['reference']
