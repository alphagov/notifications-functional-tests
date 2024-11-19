import base64
import uuid
from io import BytesIO

import pdf2image
import pytest
import pyzbar.pyzbar
from retry.api import retry_call

from config import config
from tests.functional.preview_and_dev.consts import (
    correct_letter,
    pdf_with_virus,
)
from tests.postman import (
    get_notification_by_id_via_api,
    get_pdf_for_letter_via_api,
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
def test_send_letter_notification_via_api(client_test_key):
    notification_id = send_notification_via_api(
        client_test_key,
        config["service"]["templates"]["letter"],
        config["letter_contact_data"],
        "letter",
    )

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[
            client_test_key,
            notification_id,
            NotificationStatuses.RECEIVED,
        ],
        tries=config["notification_retry_times"],
        delay=config["notification_retry_interval"],
    )
    assert_notification_body(notification_id, notification)


@recordtime
def test_send_letter_notification_with_qr_code_via_api(client_test_key):

    # Static parts length: prefix + suffix + 2 UUIDs (36*2) + 4 slashes + 6 for '?code='
    static_parts_length = len("prefix ///?code= suffix")
    notify_admin_url_length = len(config["notify_admin_url"])
    uuid_length = 36 * 2  # Length of two UUIDs

    # Calculate remaining length for '0123456789' part
    remaining_length = 499 - (static_parts_length + notify_admin_url_length + uuid_length)

    # Generate a string of '0123456789' repeated enough times, then slice it to fit the exact remaining length
    numbers_part = ("0123456789" * ((remaining_length // 10) + 1))[:remaining_length]

    qr_code_data = (
        # 499 bytes of data
        f"prefix {config['notify_admin_url']}/{numbers_part}/{uuid.uuid4()}/?code={uuid.uuid4()} suffix"
    )

    # Re-use the letter template, but we need a new paragraph for the QR code to be generated so put some newlines up
    # front. Newlines at the end move the fullstop which is part of the template out of the QR code data.
    notification = client_test_key.send_letter_notification(
        config["service"]["templates"]["letter"],
        {**config["letter_contact_data"], "content": f"\n\nqr: {qr_code_data}\n\n"},
    )
    notification_id = notification["id"]

    retry_call(
        get_notification_by_id_via_api,
        fargs=[
            client_test_key,
            notification_id,
            NotificationStatuses.RECEIVED,
        ],
        tries=config["notification_retry_times"],
        delay=config["notification_retry_interval"],
    )

    # wait until the PDF for the letter is generated
    letter_pdf = retry_call(
        get_pdf_for_letter_via_api,
        fargs=[client_test_key, notification_id],
        tries=config["pdf_generation_retry_times"],
        delay=config["pdf_generation_retry_interval"],
    )

    image = pdf2image.convert_from_bytes(letter_pdf.read())
    qr_codes = pyzbar.pyzbar.decode(image[0])

    assert len(qr_codes) == 1, f"Expected to find 1 qr code in letter - found {len(qr_codes)}?"
    assert qr_codes[0].data == qr_code_data.encode()


@recordtime
@pytest.mark.antivirus
def test_send_precompiled_letter_notification_via_api(client_test_key):
    reference = config["service_name"].replace(" ", "_") + "_delivered"

    notification_id = send_precompiled_letter_via_api(
        reference,
        client_test_key,
        BytesIO(base64.b64decode(correct_letter)),
    )

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[
            client_test_key,
            notification_id,
            NotificationStatuses.RECEIVED,
        ],
        tries=config["notification_retry_times"],
        delay=config["notification_retry_interval"],
    )

    assert reference == notification["reference"]


@recordtime
@pytest.mark.antivirus
def test_send_precompiled_letter_with_virus_notification_via_api(
    client_test_key,
):
    # This uses a file which drops the Eicar test virus into the temp directory
    # The dropper code _should_ be detected before the eicar virus

    reference = config["service_name"].replace(" ", "_") + "_virus_scan_failed"

    notification_id = send_precompiled_letter_via_api(
        reference,
        client_test_key,
        BytesIO(base64.b64decode(pdf_with_virus)),
    )

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[
            client_test_key,
            notification_id,
            NotificationStatuses.VIRUS_SCAN_FAILED,
        ],
        tries=config["notification_retry_times"],
        delay=config["notification_retry_interval"],
    )

    assert reference == notification["reference"]
