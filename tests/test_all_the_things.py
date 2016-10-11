import uuid

from notifications_python_client.notifications import NotificationsAPIClient

from config import Config

from tests.pages.rollups import get_service_templates_and_api_key_for_tests
from tests.postman import (
    send_notification_via_api,
    get_notification_by_id_via_api
)
from tests.utils import (
    get_link,
    create_temp_csv,
    get_email_body,
    remove_all_emails,
    generate_unique_email,
    do_verify,
    assert_notification_body,
)
from tests.pages import (
    MainPage,
    RegistrationPage,
    DashboardPage,
    AddServicePage,
    SendEmailTemplatePage,
    UploadCsvPage,
    SendSmsTemplatePage,
    TeamMembersPage,
    InviteUserPage,
    RegisterFromInvite,
    EditEmailTemplatePage,
    ApiKeyPage
)


def _get_email_message(profile):
    try:
        return get_email_body(profile, profile.email_notification_label)

    finally:
        remove_all_emails(email_folder=profile.email_notification_label)


# Note registration *must* run before any other tests as it registers the user for use
# in later tests and test_python_client_flow.py needs to run last as it will use templates created
# by sms and email tests
def test_everything(driver, base_url, profile):
    do_user_registration(driver, base_url, profile)

    # TODO move this to profile and setup in conftest
    test_ids = get_service_templates_and_api_key_for_tests(driver, profile)

    do_send_email_from_csv(driver, profile, test_ids)
    do_send_sms_from_csv(driver, profile, test_ids)
    do_edit_and_delete_email_template(driver, profile)

    do_test_python_client_test_api_key(driver, profile, test_ids)

    # must be last, as it signs out the user
    do_user_can_invite_someone_to_notify(driver, profile)


def do_user_registration(driver, base_url, profile):

    main_page = MainPage(driver)
    main_page.get()
    main_page.click_set_up_account()

    registration_page = RegistrationPage(driver)
    assert registration_page.is_current()

    registration_page.register(profile)

    assert driver.current_url == base_url + '/registration-continue'

    registration_link = get_link(profile, profile.registration_email_label,
                                 profile.registration_template_id,
                                 profile.email)

    driver.get(registration_link)

    do_verify(driver, profile)

    add_service_page = AddServicePage(driver)
    assert add_service_page.is_current()
    add_service_page.add_service(profile.service_name)

    dashboard_page = DashboardPage(driver)
    service_id = dashboard_page.get_service_id()
    dashboard_page.go_to_dashboard_for_service(service_id)

    assert dashboard_page.h2_is_service_name(profile.service_name)


def do_send_email_from_csv(driver, profile, test_ids):

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_email_templates()

    send_email_page = SendEmailTemplatePage(driver)
    send_email_page.click_upload_recipients()

    directory, filename = create_temp_csv(profile.email, 'email address')

    upload_csv_page = UploadCsvPage(driver)
    upload_csv_page.upload_csv(directory, filename)
    notification_id = upload_csv_page.get_notification_id_after_upload()

    client = NotificationsAPIClient(Config.NOTIFY_API_URL,
                                    test_ids['service_id'],
                                    test_ids['api_key'])

    notification = get_notification_by_id_via_api(client,
                                                  notification_id,
                                                  ['sending', 'delivered'])

    assert_notification_body(notification_id, notification)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()


def do_send_sms_from_csv(driver, profile, test_ids):

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_sms_templates()

    send_sms_page = SendSmsTemplatePage(driver)
    send_sms_page.click_upload_recipients()

    directory, filename = create_temp_csv(profile.mobile, 'phone number')

    upload_csv_page = UploadCsvPage(driver)

    upload_csv_page.upload_csv(directory, filename)

    client = NotificationsAPIClient(Config.NOTIFY_API_URL,
                                    test_ids['service_id'],
                                    test_ids['api_key'])
    notification_id = upload_csv_page.get_notification_id_after_upload()
    notification = get_notification_by_id_via_api(client,
                                                  notification_id,
                                                  ['sending', 'delivered'])

    assert_notification_body(notification_id, notification)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()


def do_edit_and_delete_email_template(driver, profile):
    test_name = 'edit/delete test'
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()
    dashboard_page.click_email_templates()

    existing_templates = [x.text for x in driver.find_elements_by_class_name('message-name')]

    all_templates_page = SendEmailTemplatePage(driver)
    all_templates_page.click_add_new_template()

    template_page = EditEmailTemplatePage(driver)
    template_page.create_template(name=test_name)

    assert test_name in [x.text for x in driver.find_elements_by_class_name('message-name')]

    all_templates_page.click_edit_template()
    template_page.click_delete()

    assert [x.text for x in driver.find_elements_by_class_name('message-name')] == existing_templates


def do_user_can_invite_someone_to_notify(driver, profile):

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

    invite_link = get_link(profile, profile.invitation_email_label, profile.invitation_template_id, invite_email)

    invite_user_page.sign_out()

    # next part of interaction is from point of view of invitee
    # i.e. after visting invite_link we'll be registering using invite_email
    # but use same mobile number and password as profile

    driver.get(invite_link)
    register_from_invite_page = RegisterFromInvite(driver)
    register_from_invite_page.fill_registration_form(invited_user_name, profile)
    register_from_invite_page.click_continue()

    do_verify(driver, profile)

    dashboard_page = DashboardPage(driver)
    service_id = dashboard_page.get_service_id()
    dashboard_page.go_to_dashboard_for_service(service_id)

    assert dashboard_page.h2_is_service_name(profile.service_name)

    dashboard_page.sign_out()


def do_test_python_client_test_api_key(driver, profile, test_ids):
    test_key = create_api_key(driver, 'test')

    remove_all_emails(email_folder=profile.email_notification_label)

    client = NotificationsAPIClient(Config.NOTIFY_API_URL, test_ids['service_id'], test_key)

    notification_id = send_notification_via_api(client, test_ids['email_template_id'], profile.email, 'email')
    notification = get_notification_by_id_via_api(client, notification_id, ['sending', 'delivered'])
    assert_notification_body(notification_id, notification)

    remove_all_emails(email_folder=profile.email_notification_label)


def create_api_key(driver, key_type):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()
    dashboard_page.click_api_keys_link()

    api_key_page = ApiKeyPage(driver)
    api_key_page.click_keys_link()
    api_key_page.click_create_key()

    api_key_page.click_key_type_radio(key_type)
    api_key_page.enter_key_name(key_type)
    api_key_page.click_continue()
    return api_key_page.get_api_key()
