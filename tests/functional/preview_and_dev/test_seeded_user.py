import base64
import urllib
import uuid
from io import BytesIO

import pytest

from retry.api import retry_call
from config import config
from selenium.common.exceptions import TimeoutException

from tests.decorators import retry_on_stale_element_exception
from tests.functional.preview_and_dev.consts import multi_page_pdf, pdf_with_virus, preview_error

from tests.postman import (
    send_notification_via_csv,
    get_notification_by_id_via_api,
    send_precompiled_letter_via_api)

from tests.test_utils import (
    assert_notification_body,
    do_edit_and_delete_email_template,
    NotificationStatuses,
    recordtime
)

from tests.pages import (
    ApiIntegrationPage,
    DashboardPage,
    SendOneRecipient,
    SmsSenderPage,
    UploadCsvPage,
    PreviewLetterPage)


@recordtime
@pytest.mark.parametrize('message_type', ['sms', 'email', 'letter'])
def test_send_csv(driver, login_seeded_user, seeded_client, seeded_client_using_test_key, message_type):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config['service']['id'])

    template_id = {
        'email': config['service']['templates']['email'],
        'sms': config['service']['templates']['sms'],
        'letter': config['service']['templates']['letter'],
    }.get(message_type)

    dashboard_stats_before = get_dashboard_stats(dashboard_page, message_type, template_id)

    upload_csv_page = UploadCsvPage(driver)
    notification_id = send_notification_via_csv(upload_csv_page, message_type, seeded=True)

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[seeded_client_using_test_key if message_type == 'letter' else seeded_client,
               notification_id,
               NotificationStatuses.RECEIVED if message_type == 'letter' else NotificationStatuses.SENT],
        tries=config['notification_retry_times'],
        delay=config['notification_retry_interval']
    )
    assert_notification_body(notification_id, notification)
    dashboard_page.go_to_dashboard_for_service(service_id=config['service']['id'])

    dashboard_stats_after = get_dashboard_stats(dashboard_page, message_type, template_id)

    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)


@recordtime
@pytest.mark.parametrize('message_type', ['sms', 'email'])
def test_edit_and_delete_template(driver, login_seeded_user, seeded_client, message_type):
    do_edit_and_delete_email_template(driver)


@recordtime
def test_send_email_to_one_recipient(driver, seeded_client, login_seeded_user):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config['service']['id'])

    message_type = 'email'

    template_id = {
        'email': config['service']['templates']['email'],
        'sms': config['service']['templates']['sms'],
    }.get(message_type)

    dashboard_stats_before = get_dashboard_stats(dashboard_page, message_type, template_id)

    send_to_one_recipient_page = SendOneRecipient(driver)

    send_to_one_recipient_page.go_to_send_one_recipient(
        config['service']['id'],
        config['service']['templates']['email']
    )

    send_to_one_recipient_page.choose_alternative_reply_to_email()
    send_to_one_recipient_page.click_continue()
    send_to_one_recipient_page.click_use_my_email()
    send_to_one_recipient_page.update_build_id()
    send_to_one_recipient_page.click_continue()

    # assert the reply to address etc is correct
    preview_rows = send_to_one_recipient_page.get_preview_contents()

    assert "From" in str(preview_rows[0].text)
    assert config['service']['name'] in str(preview_rows[0].text)
    assert "Reply to" in str(preview_rows[1].text)
    assert config['service']['email_reply_to'] in str(preview_rows[1].text)
    assert "To" in str(preview_rows[2].text)
    assert config['service']['seeded_user']['email'] in str(preview_rows[2].text)
    assert "Subject" in str(preview_rows[3].text)
    assert "Functional Tests – CSV Email" in str(preview_rows[3].text)

    send_to_one_recipient_page.click_continue()

    notification_id = dashboard_page.get_notification_id()
    one_off_email = seeded_client.get_notification_by_id(notification_id)
    assert one_off_email.get('created_by_name') == 'Preview admin tests user'

    dashboard_page.go_to_dashboard_for_service(service_id=config['service']['id'])

    dashboard_stats_after = get_dashboard_stats(dashboard_page, message_type, template_id)

    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)


@recordtime
def test_send_sms_to_one_recipient(driver, login_seeded_user):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config['service']['id'])

    template_id = config['service']['templates']['sms']

    dashboard_stats_before = get_dashboard_stats(dashboard_page, 'sms', template_id)

    send_to_one_recipient_page = SendOneRecipient(driver)
    sms_sender_page = SmsSenderPage(driver)

    send_to_one_recipient_page.go_to_send_one_recipient(config['service']['id'], template_id)

    send_to_one_recipient_page.choose_alternative_sms_sender()
    send_to_one_recipient_page.click_continue()
    send_to_one_recipient_page.click_use_my_phone_number()
    # updates the personalisation field with 'test_1234'
    send_to_one_recipient_page.update_build_id()
    send_to_one_recipient_page.click_continue()

    sms_sender = sms_sender_page.get_sms_sender()
    sms_recipient = sms_sender_page.get_sms_recipient()
    sms_content = sms_sender_page.get_sms_content()

    assert sms_sender.text == 'From: {}'.format(config['service']['sms_sender_text'])
    assert sms_recipient.text == 'To: {}'.format(config['user']['mobile'])
    assert 'The quick brown fox jumped over the lazy dog. Jenkins build id: {}.'.format('test_1234') \
        in sms_content.text

    send_to_one_recipient_page.click_continue()

    dashboard_page.go_to_dashboard_for_service(service_id=config['service']['id'])

    dashboard_stats_after = get_dashboard_stats(dashboard_page, 'sms', template_id)

    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)


def test_view_precompiled_letter_message_log_delivered(
        driver,
        login_seeded_user,
        seeded_client_using_test_key
):

    reference = "functional_tests_precompiled_" + str(uuid.uuid1()) + "_delivered"

    send_precompiled_letter_via_api(
        reference,
        seeded_client_using_test_key,
        BytesIO(base64.b64decode(multi_page_pdf))
    )

    api_integration_page = ApiIntegrationPage(driver)
    api_integration_page.go_to_api_integration_for_service(service_id=config['service']['id'])

    retry_call(
        _check_status_of_notification,
        fargs=[api_integration_page, config['service']['id'], reference, "received"],
        tries=config['notification_retry_times'],
        delay=config['notification_retry_interval']
    )

    ref_link = config['service']['id'] + "/notification/" + api_integration_page.get_notification_id()
    link = api_integration_page.get_view_letter_link()
    assert ref_link in link


def test_view_precompiled_letter_preview_delivered(
        driver,
        login_seeded_user,
        seeded_client_using_test_key
):

    reference = "functional_tests_precompiled_letter_preview_" + str(uuid.uuid1()) + "_delivered"

    notification_id = send_precompiled_letter_via_api(
        reference,
        seeded_client_using_test_key,
        BytesIO(base64.b64decode(multi_page_pdf))
    )

    api_integration_page = ApiIntegrationPage(driver)
    api_integration_page.go_to_api_integration_for_service(service_id=config['service']['id'])

    retry_call(
        _check_status_of_notification,
        fargs=[api_integration_page, config['service']['id'], reference, "received"],
        tries=config['notification_retry_times'],
        delay=config['notification_retry_interval']
    )

    api_integration_page.go_to_preview_letter()

    letter_preview_page = PreviewLetterPage(driver)
    assert letter_preview_page.is_text_present_on_page("Provided as PDF")

    # Check the pdf link looks valid
    pdf_download_link = letter_preview_page.get_download_pdf_link()

    link = config['service']['id'] + "/notification/" + notification_id + ".pdf"

    assert link in pdf_download_link

    # Check the link has a file at the end of it
    with urllib.request.urlopen(pdf_download_link) as url:
        pdf_file_data = url.read()

    assert pdf_file_data

    # check the image isn't the error page (we can't do much else)
    image_src = letter_preview_page.get_image_src()
    with urllib.request.urlopen(image_src) as url:
        image_data = url.read()

    assert base64.b64encode(image_data) != preview_error


def test_view_precompiled_letter_message_log_virus_scan_failed(
        driver,
        login_seeded_user,
        seeded_client_using_test_key
):

    reference = "functional_tests_precompiled_" + str(uuid.uuid1()) + "_delivered"

    send_precompiled_letter_via_api(
        reference,
        seeded_client_using_test_key,
        BytesIO(base64.b64decode(pdf_with_virus))
    )

    api_integration_page = ApiIntegrationPage(driver)

    retry_call(
        _check_status_of_notification,
        fargs=[api_integration_page, config['service']['id'], reference, "virus-scan-failed"],
        tries=config['notification_retry_times'],
        delay=config['notification_retry_interval']
    )

    ref_link = config['service']['id'] + "/notification/" + api_integration_page.get_notification_id()
    link = api_integration_page.get_view_letter_link()
    assert ref_link not in link


def _check_status_of_notification(page, notify_research_service_id, reference_to_check, status_to_check):
    page.go_to_api_integration_for_service(service_id=notify_research_service_id)
    client_reference = page.get_client_reference()
    assert reference_to_check == client_reference
    assert status_to_check == page.get_status_from_message()


@retry_on_stale_element_exception
def get_dashboard_stats(dashboard_page, message_type, template_id):
    return {
        'total_messages_sent': dashboard_page.get_total_message_count(message_type),
        'template_messages_sent': _get_template_count(dashboard_page, template_id)
    }


def assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after):
    for k in dashboard_stats_before.keys():
        assert dashboard_stats_after[k] == dashboard_stats_before[k] + 1


def _get_template_count(dashboard_page, template_id):
    try:
        template_messages_count = dashboard_page.get_template_message_count(template_id)
    except TimeoutException:
        return 0  # template count may not exist yet if no messages sent
    else:
        return template_messages_count
