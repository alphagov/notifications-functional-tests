import pytest

from tests.pages import DashboardPage, SmsSenderPage
from tests.test_utils import (
    do_user_can_add_reply_to_email_to_service,
    do_user_can_invite_someone_to_notify,
    do_user_can_update_reply_to_email_to_service,
    do_user_registration,
    recordtime,
)


@pytest.fixture(scope="module", autouse=True)
@recordtime
def register_user(_driver):
    # has to use _driver as this is at module level (`driver` fixture is at function level, and just handles taking
    # the screenshot on failure)
    do_user_registration(_driver)


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
def test_invite_flow(driver):
    do_user_can_invite_someone_to_notify(driver, basic_view=False)
    do_user_can_invite_someone_to_notify(driver, basic_view=True)


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
def test_can_add_and_update_reply_to(driver):
    do_user_can_add_reply_to_email_to_service(driver)
    do_user_can_update_reply_to_email_to_service(driver)


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
def test_user_can_add_sms_sender_to_service(driver):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()

    service_id = dashboard_page.get_service_id()

    sms_sender_page = SmsSenderPage(driver)

    sms_sender_page.go_to_add_text_message_sender(service_id)
    sms_sender_page.insert_sms_sender("second")
    sms_sender_page.click_save_sms_sender()

    main_content = sms_sender_page.get_sms_senders()

    assert "first \u2002 (default)" in main_content.text
    assert "second" in main_content.text
    assert "second \u2002 (default)" not in main_content.text

    dashboard_page.go_to_dashboard_for_service(service_id)


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
def test_can_update_sms_sender_of_service(driver):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()

    service_id = dashboard_page.get_service_id()

    sms_sender_page = SmsSenderPage(driver)

    sms_sender_page.go_to_text_message_senders(service_id)
    sms_sender_page.click_change_link_for_first_sms_sender()
    sms_sender_page.insert_sms_sender("first")
    sms_sender_page.click_save_sms_sender()

    main_content = sms_sender_page.get_sms_senders()

    assert "first \u2002 (default)" in main_content.text

    dashboard_page.go_to_dashboard_for_service(service_id)
