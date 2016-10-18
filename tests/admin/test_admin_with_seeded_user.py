import pytest

from selenium.common.exceptions import TimeoutException

from tests.postman import (
    send_notification_via_csv,
    get_notification_by_id_via_api)


from tests.utils import (
    do_user_registration,
    do_user_can_invite_someone_to_notify,
    assert_notification_body
    )

from tests.pages import (
    DashboardPage,
    UploadCsvPage
)


def test_registration_and_invite_flow(driver, profile, base_url):
    do_user_registration(driver, profile, base_url)
    do_user_can_invite_someone_to_notify(driver, profile)


@pytest.mark.parametrize('message_type', ['sms', 'email'])
def test_send_csv(driver, profile, login_seeded_user, seeded_client, message_type):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()
    template_id = profile.email_template_id if message_type == 'email' else profile.sms_template_id

    dashboard_stats_before = get_dashboard_stats(dashboard_page, message_type, template_id)

    upload_csv_page = UploadCsvPage(driver)
    notification_id = send_notification_via_csv(profile, upload_csv_page, message_type, seeded=True)
    notification = get_notification_by_id_via_api(
        seeded_client,
        notification_id,
        ['sending', 'delivered']
    )
    assert_notification_body(notification_id, notification)
    dashboard_page.go_to_dashboard_for_service()

    dashboard_stats_after = get_dashboard_stats(dashboard_page, message_type, template_id)

    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)


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
