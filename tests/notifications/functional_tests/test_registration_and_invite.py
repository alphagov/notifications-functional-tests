import pytest
from selenium.common.exceptions import TimeoutException

from config import config
from tests.pages import (
    ChangeName,
    DashboardPage,
    ServiceJoinRequestApprovePage,
    ServiceJoinRequestChoosePermissionsPage,
    ServiceJoinRequestChooseServicePage,
    ServiceJoinRequestJoinAskPage,
    ServiceSettingsPage,
    SignInPage,
    SmsSenderPage,
    YourServicesPage,
)
from tests.pages.rollups import sign_in
from tests.test_utils import (
    do_user_add_new_service,
    do_user_can_add_reply_to_email_to_service,
    do_user_can_invite_someone_to_notify,
    do_user_can_update_reply_to_email_to_service,
    do_user_registration,
    get_link,
    recordtime,
)


@pytest.fixture()
def user_register_or_sign_in(driver):
    sign_in_page = SignInPage(driver)
    sign_in_page.get()

    try:
        sign_in_page.wait_until_current()
    except TimeoutException:
        # if we didn't get to the sign_in_page, it's probably because we're already logged in.
        # try logging out before proceeding
        _sign_in_again(driver)
    else:
        do_user_registration(driver)
        do_user_add_new_service(driver)


def _sign_in_again(driver):
    # sign back in as the original service user
    dashboard_page = DashboardPage(driver)
    dashboard_page.sign_out()
    dashboard_page.wait_until_url_contains(config["notify_admin_url"])

    sign_in(driver, account_type="normal")

    service_id = dashboard_page.get_service_id()
    dashboard_page.go_to_dashboard_for_service(service_id)


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
def test_invite_flow(driver, user_register_or_sign_in):
    do_user_can_invite_someone_to_notify(driver, basic_view=False)

    _sign_in_again(driver)

    do_user_can_invite_someone_to_notify(driver, basic_view=True)


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
@pytest.mark.skipif("not config['enable_edit_reply_to']")  # condition as string for deferred evaluation
def test_can_add_and_update_reply_to(driver, user_register_or_sign_in):
    do_user_can_add_reply_to_email_to_service(driver)
    do_user_can_update_reply_to_email_to_service(driver)


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
def test_can_add_and_update_sms_sender_of_service(driver, user_register_or_sign_in):
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
def test_change_service_name(driver, user_register_or_sign_in):
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


def _do_approver_sign_in(driver):
    requested_user_email = config["service"]["seeded_user"]["email"]
    sign_in(driver, account_type="seeded")
    invite_link = get_link(config["notify_templates"]["request_invite_to_service_template_id"], requested_user_email)
    driver.get(invite_link)


def _do_request_to_join_service(driver):
    add_service_page = YourServicesPage(driver)
    add_service_page.wait_until_current()
    add_service_page.join_existing_service()

    add_service_page.wait_until_url_contains("/join-a-service/choose")

    choose_service_page = ServiceJoinRequestChooseServicePage(driver)
    if choose_service_page.check_if_search_input_exists():
        choose_service_page.search_service_input = "Functional tests"
    choose_service_page.go_to_selected_service()

    join_ask_page = ServiceJoinRequestJoinAskPage(driver)
    join_ask_page.select_approver_user_checkbox()
    join_ask_page.request_reason_input = "Test join service reason"
    join_ask_page.ask_to_join_service()

    join_ask_page.wait_until_url_contains("/join/you-have-asked?number_of_users_emailed=1")

    add_service_page.sign_out()


def _do_approver_approved_request(driver):
    _do_approver_sign_in(driver)

    join_service_request_approve_page = ServiceJoinRequestApprovePage(driver)
    join_service_request_approve_page.continue_to_next_step()

    choose_permissions_page = ServiceJoinRequestChoosePermissionsPage(driver)
    choose_permissions_page.fill_invitation_form()
    choose_permissions_page.select_sms_auth_form()
    choose_permissions_page.save_permissions()
    choose_permissions_page.wait_until_url_contains("/users")


def _do_approver_rejected_request(driver):
    _do_approver_sign_in(driver)

    join_service_request_approve_page = ServiceJoinRequestApprovePage(driver)
    join_service_request_approve_page.select_rejected_option()
    join_service_request_approve_page.continue_to_next_step()

    join_service_request_approve_page.wait_until_url_contains("/refused")


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
def test_join_existing_service_rejected_flow(driver, user_register_or_sign_in):
    _do_request_to_join_service(driver)
    _do_approver_rejected_request(driver)


@recordtime
@pytest.mark.xdist_group(name="registration-flow")
def test_join_existing_service_approved_flow(driver, user_register_or_sign_in):
    _do_request_to_join_service(driver)
    _do_approver_approved_request(driver)
