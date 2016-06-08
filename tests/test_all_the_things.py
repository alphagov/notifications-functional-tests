import pytest
import uuid

from requests import session

from tests.utils import (
    get_link,
    create_temp_csv,
    get_email_body,
    remove_all_emails,
    get_sms_via_heroku,
    generate_unique_email,
    get_verify_code
)

from tests.pages import (
    MainPage,
    RegistrationPage,
    VerifyPage,
    DashboardPage,
    AddServicePage,
    SendEmailTemplatePage,
    EditEmailTemplatePage,
    UploadCsvPage,
    SendSmsTemplatePage,
    EditSmsTemplatePage,
    TeamMembersPage,
    InviteUserPage,
    RegisterFromInvite,
    TwoFactorPage
)


def _get_email_message(profile):
    try:
        return get_email_body(profile, profile.email_notification_label)
    except Exception as e:
        pytest.fail("Couldn't get notification email")
    finally:
        remove_all_emails(email_folder=profile.email_notification_label)


def test_everything(driver, base_url, profile):
    do_user_registration(driver, base_url, profile)
    do_create_email_template_and_send_from_csv(driver, base_url, profile)
    do_create_sms_template_and_send_from_csv(driver, base_url, profile)
    do_user_can_invite_someone_to_notify(driver, base_url, profile)


def do_user_registration(driver, base_url, profile):

    main_page = MainPage(driver)
    main_page.get()
    main_page.click_set_up_account()

    registration_page = RegistrationPage(driver)
    assert registration_page.is_current()

    registration_page.register(profile)

    assert driver.current_url == base_url + '/registration-continue'

    registration_link = get_link(profile, profile.registration_email_label)

    driver.get(registration_link)
    verify_code = get_verify_code()

    verify_page = VerifyPage(driver)
    assert verify_page.is_current()
    verify_page.verify(verify_code)

    add_service_page = AddServicePage(driver)
    assert add_service_page.is_current()
    add_service_page.add_service(profile.service_name)

    dashboard_page = DashboardPage(driver)
    service_id = dashboard_page.get_service_id()
    dashboard_page.go_to_dashboard_for_service(service_id)

    assert dashboard_page.h2_is_service_name(profile.service_name)


def do_create_email_template_and_send_from_csv(driver, base_url, profile):

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_email_templates()

    email_template_page = SendEmailTemplatePage(driver)
    email_template_page.click_add_new_template()

    new_email_template = EditEmailTemplatePage(driver)
    new_email_template.create_template()

    send_email_page = SendEmailTemplatePage(driver)
    send_email_page.click_send_from_csv_link()

    directory, filename = create_temp_csv(profile.email, 'email address')

    upload_csv_page = UploadCsvPage(driver)
    upload_csv_page.upload_csv(directory, filename)

    email_body = _get_email_message(profile)
    assert "The quick brown fox jumped over the lazy dog" in email_body
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()


def do_create_sms_template_and_send_from_csv(driver, base_url, profile):

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_sms_templates()

    sms_template_page = SendSmsTemplatePage(driver)
    sms_template_page.click_add_new_template()

    new_sms_template = EditSmsTemplatePage(driver)
    new_sms_template.create_template()

    send_sms_page = SendSmsTemplatePage(driver)
    send_sms_page.click_send_from_csv_link()

    directory, filename = create_temp_csv(profile.mobile, 'phone number')

    upload_csv_page = UploadCsvPage(driver)
    upload_csv_page.upload_csv(directory, filename)

    # check we are on jobs page and status is sending?
    # assert '/jobs' in post_check_sms.url

    message = get_sms_via_heroku(session())
    assert "The quick brown fox jumped over the lazy dog" in message
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()


def do_user_can_invite_someone_to_notify(driver, base_url, profile):

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_team_members_link()

    team_members_page = TeamMembersPage(driver)
    assert team_members_page.h1_is_team_members()
    team_members_page.click_invite_user()

    invite_user_page = InviteUserPage(driver)

    invited_user_randomness = str(uuid.uuid1())
    invited_user_name = 'Invited User ' + invited_user_randomness
    invite_email = generate_unique_email(profile.email, invited_user_randomness)

    invite_user_page.fill_invitation_form(invite_email, send_messages=True)
    invite_user_page.send_invitation()

    invite_link = get_link(profile, profile.invitation_email_label)

    invite_user_page.sign_out()

    # next part of interaction is from point of view of invitee
    # i.e. after visting invite_link we'll be registering using invite_email
    # but use same mobile number and password as profile

    driver.get(invite_link)
    register_from_invite_page = RegisterFromInvite(driver)
    register_from_invite_page.fill_registration_form(invited_user_name, profile)
    register_from_invite_page.click_continue()

    two_factor_page = TwoFactorPage(driver)
    verify_code = get_verify_code()
    two_factor_page.verify(verify_code)

    dashboard_page = DashboardPage(driver)
    service_id = dashboard_page.get_service_id()
    dashboard_page.go_to_dashboard_for_service(service_id)

    assert dashboard_page.h2_is_service_name(profile.service_name)

    dashboard_page.sign_out()
