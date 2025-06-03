import pytest
from selenium.common.exceptions import TimeoutException

from config import config
from tests.pages import (
    ServiceJoinRequestApprovePage,
    ServiceJoinRequestChoosePermissionsPage,
    ServiceJoinRequestChooseServicePage,
    ServiceJoinRequestJoinAskPage,
    SignInPage,
    YourServicesPage,
)
from tests.pages.rollups import sign_in
from tests.test_utils import do_user_registration, get_link, recordtime


@pytest.fixture(autouse=True)
def user_register_or_sign_in(driver):
    sign_in_page = SignInPage(driver)
    sign_in_page.get()

    try:
        sign_in_page.wait_until_current()
    except TimeoutException:
        # if we didn't get to the sign_in_page, it's probably because we're already logged in.
        # try logging out before proceeding
        _do_requester_sign_in(driver)
    else:
        do_user_registration(driver)


def _do_requester_sign_in(driver):
    # sign back in as requester (normal user)
    dashboard_page = YourServicesPage(driver)
    dashboard_page.sign_out()
    dashboard_page.wait_until_url_contains(config["notify_admin_url"])

    sign_in(driver, account_type="normal")


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
@pytest.mark.xdist_group(name="join-service-request-flow")
def test_join_existing_service_rejected_flow(driver, create_seeded_user):
    _do_request_to_join_service(driver)
    _do_approver_rejected_request(driver)


@recordtime
@pytest.mark.xdist_group(name="join-service-request-flow")
def test_join_existing_service_approved_flow(driver, create_seeded_user):
    _do_request_to_join_service(driver)
    _do_approver_approved_request(driver)
