import base64
import urllib
import uuid
from io import BytesIO

import pytest

from retry.api import retry_call
from config import Config
from selenium.common.exceptions import TimeoutException

from tests.decorators import retry_on_stale_element_exception
from tests.functional.preview_and_dev.consts import one_page_pdf, pdf_with_virus, preview_error

from tests.postman import (
    send_notification_via_csv,
    get_notification_by_id_via_api,
    NotificationStatuses,
    send_precompiled_letter_via_api)

from tests.test_utils import (
    assert_notification_body,
    do_edit_and_delete_email_template,
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
def test_send_csv(driver, profile, login_seeded_user, seeded_client, seeded_client_using_test_key, message_type):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=profile.notify_research_service_id)

    template_id = {
        'email': profile.jenkins_build_email_template_id,
        'sms': profile.jenkins_build_sms_template_id,
        'letter': profile.jenkins_build_letter_template_id,
    }.get(message_type)

    dashboard_stats_before = get_dashboard_stats(dashboard_page, message_type, template_id)

    upload_csv_page = UploadCsvPage(driver)
    notification_id = send_notification_via_csv(profile, upload_csv_page, message_type, seeded=True)

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[seeded_client_using_test_key if message_type == 'letter' else seeded_client,
               notification_id,
               NotificationStatuses.RECEIVED if message_type == 'letter' else NotificationStatuses.SENT],
        tries=Config.NOTIFICATION_RETRY_TIMES,
        delay=Config.NOTIFICATION_RETRY_INTERVAL
    )
    assert_notification_body(notification_id, notification)
    dashboard_page.go_to_dashboard_for_service(service_id=profile.notify_research_service_id)

    dashboard_stats_after = get_dashboard_stats(dashboard_page, message_type, template_id)

    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)


@recordtime
@pytest.mark.parametrize('message_type', ['sms', 'email'])
def test_edit_and_delete_template(driver, profile, login_seeded_user, seeded_client, message_type):
    do_edit_and_delete_email_template(profile, driver)


@recordtime
def test_send_email_to_one_recipient(driver, profile, base_url, seeded_client, login_seeded_user):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=profile.notify_research_service_id)

    message_type = 'email'

    template_id = {
        'email': profile.jenkins_build_email_template_id,
        'sms': profile.jenkins_build_sms_template_id,
    }.get(message_type)

    dashboard_stats_before = get_dashboard_stats(dashboard_page, message_type, template_id)

    send_to_one_recipient_page = SendOneRecipient(driver)

    send_to_one_recipient_page.go_to_send_one_recipient(
        profile.notify_research_service_id,
        profile.jenkins_build_email_template_id
    )

    send_to_one_recipient_page.choose_alternative_reply_to_email()
    send_to_one_recipient_page.click_continue()
    send_to_one_recipient_page.click_use_my_email()
    send_to_one_recipient_page.update_build_id()
    send_to_one_recipient_page.click_continue()

    # assert the reply to address etc is correct
    preview_rows = send_to_one_recipient_page.get_preview_contents()

    assert "From" in str(preview_rows[0].text)
    assert profile.notify_research_service_name in str(preview_rows[0].text)
    assert "Reply to" in str(preview_rows[1].text)
    assert profile.notify_research_email_reply_to in str(preview_rows[1].text)
    assert "To" in str(preview_rows[2].text)
    assert profile.notify_research_service_email in str(preview_rows[2].text)
    assert "Subject" in str(preview_rows[3].text)
    assert "Functional Tests – CSV Email" in str(preview_rows[3].text)

    send_to_one_recipient_page.click_continue()

    dashboard_page.go_to_dashboard_for_service(service_id=profile.notify_research_service_id)

    dashboard_stats_after = get_dashboard_stats(dashboard_page, message_type, template_id)

    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)


@recordtime
def test_send_sms_to_one_recipient(driver, profile, login_seeded_user):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=profile.notify_research_service_id)

    template_id = profile.jenkins_build_sms_template_id

    dashboard_stats_before = get_dashboard_stats(dashboard_page, 'sms', template_id)

    send_to_one_recipient_page = SendOneRecipient(driver)
    sms_sender_page = SmsSenderPage(driver)

    send_to_one_recipient_page.go_to_send_one_recipient(profile.notify_research_service_id, template_id)

    send_to_one_recipient_page.choose_alternative_sms_sender()
    send_to_one_recipient_page.click_continue()
    send_to_one_recipient_page.click_use_my_phone_number()
    # updates the personalisation field with 'test_1234'
    send_to_one_recipient_page.update_build_id()
    send_to_one_recipient_page.click_continue()

    sms_sender = sms_sender_page.get_sms_sender()
    sms_recipient = sms_sender_page.get_sms_recipient()
    sms_content = sms_sender_page.get_sms_content()

    assert sms_sender.text == 'From: {}'.format(profile.notify_research_sms_sender)
    assert sms_recipient.text == 'To: {}'.format(profile.mobile)
    assert 'The quick brown fox jumped over the lazy dog. Jenkins build id: {}.'.format('test_1234') \
        in sms_content.text

    send_to_one_recipient_page.click_continue()

    dashboard_page.go_to_dashboard_for_service(service_id=profile.notify_research_service_id)

    dashboard_stats_after = get_dashboard_stats(dashboard_page, 'sms', template_id)

    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)


def test_view_precompiled_letter_message_log_delivered(
        driver,
        profile,
        login_seeded_user,
        seeded_client_using_test_key
):

    reference = "functional_tests_precompiled_" + str(uuid.uuid1()) + "_delivered"

    send_precompiled_letter_via_api(
        reference,
        seeded_client_using_test_key,
        BytesIO(base64.b64decode(one_page_pdf))
    )

    api_integration_page = ApiIntegrationPage(driver)
    api_integration_page.go_to_api_integration_for_service(service_id=profile.notify_research_service_id)

    retry_call(
        _check_status_of_notification,
        fargs=[api_integration_page, profile.notify_research_service_id, reference, "delivered"],
        tries=Config.NOTIFICATION_RETRY_TIMES,
        delay=Config.NOTIFICATION_RETRY_INTERVAL
    )

    ref_link = profile.notify_research_service_id + "/notification/" + api_integration_page.get_notification_id()
    link = api_integration_page.get_view_letter_link()
    assert ref_link in link


def test_view_precompiled_letter_preview_delivered(
        driver,
        profile,
        login_seeded_user,
        seeded_client_using_test_key
):

    reference = "functional_tests_precompiled_letter_preview_" + str(uuid.uuid1()) + "_delivered"

    notification_id = send_precompiled_letter_via_api(
        reference,
        seeded_client_using_test_key,
        BytesIO(base64.b64decode(one_page_pdf))
    )

    api_integration_page = ApiIntegrationPage(driver)
    api_integration_page.go_to_api_integration_for_service(service_id=profile.notify_research_service_id)

    retry_call(
        _check_status_of_notification,
        fargs=[api_integration_page, profile.notify_research_service_id, reference, "delivered"],
        tries=Config.NOTIFICATION_RETRY_TIMES,
        delay=Config.NOTIFICATION_RETRY_INTERVAL
    )

    api_integration_page.go_to_preview_letter()

    letter_preview_page = PreviewLetterPage(driver)
    assert letter_preview_page.is_text_present_on_page("Provided as PDF, sent on")

    # Check the pdf link looks valid
    pdf_download_link = letter_preview_page.get_download_pdf_link()

    link = profile.notify_research_service_id + "/notification/" + notification_id + ".pdf"

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
        profile,
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
        fargs=[api_integration_page, profile.notify_research_service_id, reference, "virus-scan-failed"],
        tries=Config.NOTIFICATION_RETRY_TIMES,
        delay=Config.NOTIFICATION_RETRY_INTERVAL
    )

    ref_link = profile.notify_research_service_id + "/notification/" + api_integration_page.get_notification_id()
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
