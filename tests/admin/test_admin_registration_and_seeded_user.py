import pytest

from retry.api import retry_call
from config import Config
from selenium.common.exceptions import TimeoutException

from tests.decorators import retry_on_stale_element_exception

from tests.postman import (
    send_notification_via_csv,
    get_notification_by_id_via_api
)

from tests.test_utils import (
    assert_notification_body,
    do_edit_and_delete_email_template,
    do_user_can_add_reply_to_email_to_service,
    do_user_can_invite_someone_to_notify,
    do_user_registration,
    recordtime
)

from tests.pages import (
    DashboardPage,
    SendOneRecipient,
    UploadCsvPage)


@recordtime
def test_registration_and_invite_flow(driver, profile, base_url):
    do_user_registration(driver, profile, base_url)
    do_user_can_add_reply_to_email_to_service(driver)
    do_user_can_invite_someone_to_notify(driver, profile, base_url)


@recordtime
@pytest.mark.parametrize('message_type', ['sms', 'email'])
def test_send_csv(driver, profile, login_seeded_user, seeded_client, message_type):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()

    template_id = {
        'email': profile.jenkins_build_email_template_id,
        'sms': profile.jenkins_build_sms_template_id,
    }.get(message_type)

    dashboard_stats_before = get_dashboard_stats(dashboard_page, message_type, template_id)

    upload_csv_page = UploadCsvPage(driver)
    notification_id = send_notification_via_csv(profile, upload_csv_page, message_type, seeded=True)

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[seeded_client, notification_id, ['sending', 'delivered']],
        tries=Config.NOTIFICATION_RETRY_TIMES,
        delay=Config.NOTIFICATION_RETRY_INTERVAL
    )
    assert_notification_body(notification_id, notification)
    dashboard_page.go_to_dashboard_for_service()

    dashboard_stats_after = get_dashboard_stats(dashboard_page, message_type, template_id)

    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)


@recordtime
@pytest.mark.parametrize('message_type', ['sms', 'email'])
def test_edit_and_delete_template(driver, profile, login_seeded_user, seeded_client, message_type):
    do_edit_and_delete_email_template(driver)


@recordtime
def test_send_email_to_one_recipient(driver, profile, base_url, seeded_client, login_seeded_user):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()

    message_type = 'email'

    template_id = {
        'email': profile.jenkins_build_email_template_id,
        'sms': profile.jenkins_build_sms_template_id,
    }.get(message_type)

    dashboard_stats_before = get_dashboard_stats(dashboard_page, message_type, template_id)

    send = SendOneRecipient(driver)

    send.go_to_send_one_recipient(
        profile.notify_research_service_id,
        profile.jenkins_build_email_template_id
    )

    send.choose_alternative_reply_to_email()
    send.click_continue()
    send.click_use_my_email()
    send.update_build_id()
    send.click_continue()

    # assert the reply to address etc is correct
    preview_rows = send.get_preview_contents()

    assert "From" in str(preview_rows[0].text)
    assert profile.notify_research_service_name in str(preview_rows[0].text)
    assert "Reply to" in str(preview_rows[1].text)
    assert profile.notify_research_email_reply_to in str(preview_rows[1].text)
    assert "To" in str(preview_rows[2].text)
    assert profile.notify_research_service_email in str(preview_rows[2].text)
    assert "Subject" in str(preview_rows[3].text)
    assert "Functional Tests – CSV Email" in str(preview_rows[3].text)

    send.click_continue()

    dashboard_page.go_to_dashboard_for_service()

    dashboard_stats_after = get_dashboard_stats(dashboard_page, message_type, template_id)

    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)


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
