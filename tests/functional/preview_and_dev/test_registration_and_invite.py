import pytest

from config import config
from tests.pages import (
    ChangeName,
    DashboardPage,
    ServiceSettingsPage,
    SmsSenderPage,
)
from tests.pages.rollups import sign_in
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


def _sign_in_again(driver):
    # sign back in as the original service user
    dashboard_page = DashboardPage(driver)
    dashboard_page.sign_out()
    dashboard_page.wait_until_url_is(config["notify_admin_url"])

    sign_in(driver, account_type="normal")

    service_id = dashboard_page.get_service_id()
    dashboard_page.go_to_dashboard_for_service(service_id)


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
@pytest.mark.dev
def test_invite_flow(driver):
    do_user_can_invite_someone_to_notify(driver, basic_view=False)

    _sign_in_again(driver)

    do_user_can_invite_someone_to_notify(driver, basic_view=True)

    _sign_in_again(driver)


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
@pytest.mark.dev
def test_can_add_and_update_reply_to(driver):
    do_user_can_add_reply_to_email_to_service(driver)
    do_user_can_update_reply_to_email_to_service(driver)


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
@pytest.mark.dev
def test_can_add_and_update_sms_sender_of_service(driver):
    dashboard_page = DashboardPage(driver)
    sms_sender_page = SmsSenderPage(driver)

    dashboard_page.go_to_dashboard_for_service()
    service_id = dashboard_page.get_service_id()

    # add first
    sms_sender_page.go_to_text_message_senders(service_id)
    sms_sender_page.click_change_link_for_first_sms_sender()
    sms_sender_page.insert_sms_sender("first")
    sms_sender_page.click_save_sms_sender()

    main_content = sms_sender_page.get_sms_senders()

    assert "first \u2002 (default)" in main_content.text

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
@pytest.mark.dev
def test_change_service_name(driver):
    old_name = config["service_name"]
    new_name = f"{old_name} (renamed)"

    dashboard_page = DashboardPage(driver)
    service_settings = ServiceSettingsPage(driver)
    change_name = ChangeName(driver)

    # make sure the service is actually named what we expect
    assert dashboard_page.get_service_name() == old_name

    dashboard_page.go_to_dashboard_for_service()
    dashboard_page.click_settings()

    service_settings.go_to_change_service_name()

    change_name.enter_new_name(new_name)
    change_name.click_save()

    dashboard_page.go_to_dashboard_for_service()
    assert dashboard_page.get_service_name() == new_name

    # change the name back. it's probably not essential that this happens
    dashboard_page.click_settings()
    service_settings.go_to_change_service_name()
    change_name.enter_new_name(old_name)
    change_name.click_save()

    dashboard_page.go_to_dashboard_for_service()
    assert dashboard_page.get_service_name() == old_name
