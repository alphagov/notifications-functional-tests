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
    create_email_template,
    create_sms_template,
    delete_template,
    go_to_templates_page,
    NotificationStatuses,
    recordtime,
    send_notification_to_one_recipient
)

from tests.pages.rollups import sign_in, sign_in_email_auth

from tests.pages import (
    ApiIntegrationPage,
    DashboardPage,
    ShowTemplatesPage,
    EditEmailTemplatePage,
    UploadCsvPage,
    PreviewLetterPage,
    ViewFolderPage,
    ManageFolderPage,
    TeamMembersPage,
    InviteUserPage,
    ChangeName,
    ServiceSettingsPage
)


@recordtime
@pytest.mark.parametrize('message_type', ['sms', 'email', pytest.param('letter', marks=pytest.mark.template_preview)])
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
def test_edit_and_delete_email_template(driver, login_seeded_user, seeded_client):
    test_name = 'edit/delete email template test'
    go_to_templates_page(driver)
    existing_templates = [x.text for x in driver.find_elements_by_class_name('message-name')]

    create_email_template(driver, name=test_name, content=None)
    go_to_templates_page(driver)
    assert test_name in [x.text for x in driver.find_elements_by_class_name('message-name')]

    delete_template(driver, test_name)
    assert [x.text for x in driver.find_elements_by_class_name('message-name')] == existing_templates


@recordtime
def test_edit_and_delete_sms_template(driver, login_seeded_user, seeded_client):
    test_name = 'edit/delete sms template test'
    go_to_templates_page(driver)
    existing_templates = [x.text for x in driver.find_elements_by_class_name('message-name')]

    create_sms_template(driver, name=test_name, content=None)
    go_to_templates_page(driver)
    assert test_name in [x.text for x in driver.find_elements_by_class_name('message-name')]

    delete_template(driver, test_name)
    assert [x.text for x in driver.find_elements_by_class_name('message-name')] == existing_templates


@recordtime
def test_send_email_with_placeholders_to_one_recipient(
    driver, seeded_client, login_seeded_user
):
    go_to_templates_page(driver)
    template_name = "email with placeholders" + str(uuid.uuid4())
    content = "Hi ((name)), Is ((email address)) your email address? We want to send you some ((things))"
    template_id = create_email_template(driver, name=template_name, content=content)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config['service']['id'])
    dashboard_stats_before = get_dashboard_stats(dashboard_page, 'email', template_id)

    placeholders = send_notification_to_one_recipient(
        driver, template_name, "email", test=False, recipient_data='anne@example.com', placeholders_number=2
    )
    assert list(placeholders[0].keys()) == ["name"]
    assert list(placeholders[1].keys()) == ["things"]

    dashboard_page.click_continue()
    notification_id = dashboard_page.get_notification_id()
    one_off_email = seeded_client.get_notification_by_id(notification_id)
    assert one_off_email.get('created_by_name') == 'Preview admin tests user'

    dashboard_page.go_to_dashboard_for_service(service_id=config['service']['id'])
    dashboard_stats_after = get_dashboard_stats(dashboard_page, 'email', template_id)
    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)

    placeholders_test = send_notification_to_one_recipient(
        driver, template_name, "email", test=True, placeholders_number=2
    )
    assert list(placeholders_test[0].keys()) == ["name"]
    assert list(placeholders_test[1].keys()) == ["things"]

    delete_template(driver, template_name)


@recordtime
def test_send_sms_with_placeholders_to_one_recipient(
    driver, seeded_client, login_seeded_user
):
    go_to_templates_page(driver)
    template_name = "sms with placeholders" + str(uuid.uuid4())
    content = "Hi ((name)), Is ((phone number)) your mobile number? We want to send you some ((things))"
    template_id = create_sms_template(driver, name=template_name, content=content)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config['service']['id'])
    dashboard_stats_before = get_dashboard_stats(dashboard_page, 'sms', template_id)

    placeholders = send_notification_to_one_recipient(
        driver, template_name, "sms", test=False, recipient_data='07700900998', placeholders_number=2
    )
    assert list(placeholders[0].keys()) == ["name"]
    assert list(placeholders[1].keys()) == ["things"]

    dashboard_page.click_continue()
    dashboard_page.go_to_dashboard_for_service(service_id=config['service']['id'])
    dashboard_stats_after = get_dashboard_stats(dashboard_page, 'sms', template_id)
    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)

    placeholders_test = send_notification_to_one_recipient(
        driver, template_name, "sms", test=True, placeholders_number=2
    )
    assert list(placeholders_test[0].keys()) == ["name"]
    assert list(placeholders_test[1].keys()) == ["things"]

    delete_template(driver, template_name)


@pytest.mark.template_preview
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


@pytest.mark.template_preview
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


def test_creating_moving_and_deleting_template_folders(driver, login_seeded_user):
    # create new template
    template_name = 'template-for-folder-test {}'.format(uuid.uuid4())
    folder_name = 'test-folder {}'.format(uuid.uuid4())

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config['service']['id'])
    dashboard_page.click_templates()

    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_add_new_template()
    show_templates_page.select_email()

    edit_template_page = EditEmailTemplatePage(driver)
    edit_template_page.create_template(name=template_name)
    template_id = edit_template_page.get_template_id()
    edit_template_page.click_templates()

    # create folder using add to new folder
    show_templates_page.select_template_checkbox(template_id)
    show_templates_page.add_to_new_folder(folder_name)

    # navigate into folder
    show_templates_page.click_template_by_link_text(folder_name)

    # rename folder step
    view_folder_page = ViewFolderPage(driver)
    view_folder_page.click_manage_folder()

    manage_folder_page = ManageFolderPage(driver)
    new_folder_name = folder_name + '-new'
    manage_folder_page.set_name(new_folder_name)
    view_folder_page.assert_name_equals(new_folder_name)

    # try to delete folder
    view_folder_page.click_manage_folder()
    manage_folder_page.delete_folder()  # fails due to not being empty

    # check error message visible
    assert manage_folder_page.get_errors() == 'You must empty this folder before you can delete it'

    # move template out of folder
    view_folder_page.select_template_checkbox(template_id)
    view_folder_page.move_to_root_template_folder()

    # delete folder
    view_folder_page.click_manage_folder()
    manage_folder_page.delete_folder()
    manage_folder_page.confirm_delete_folder()
    # assert folder not visible
    assert new_folder_name not in [x.text for x in driver.find_elements_by_class_name('message-name')]

    # delete template
    show_templates_page.click_template_by_link_text(template_name)
    edit_template_page.click_delete()

    assert template_name not in [x.text for x in driver.find_elements_by_class_name('message-name')]


def test_template_folder_permissions(driver, login_seeded_user):
    family_id = uuid.uuid4()
    folder_names = [
        'test-parent-folder {}'.format(family_id),
        'test-child-folder {}'.format(family_id),
        'test-grandchild-folder {}'.format(family_id),
    ]
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config['service']['id'])
    dashboard_page.click_templates()
    show_templates_page = ShowTemplatesPage(driver)
    # a loop to create a folder structure with parent folder, child folder and grandchild folder,
    # each folder with one template in it
    for folder_name in folder_names:
        # create a new folder
        show_templates_page.click_add_new_folder(folder_name)

        show_templates_page.click_template_by_link_text(folder_name)
        # create a new template
        show_templates_page.click_add_new_template()
        show_templates_page.select_email()

        edit_template_page = EditEmailTemplatePage(driver)
        edit_template_page.create_template(name=(folder_name + "_template"))
        # go back to view folder page
        edit_template_page.click_folder_path(folder_name)

    # go to Team members page
    dashboard_page.click_team_members_link()
    team_members_page = TeamMembersPage(driver)
    # edit colleague's permissions so child folder is invisible
    team_members_page.click_edit_team_member(config['service']['email_auth_account'])
    edit_team_member_page = InviteUserPage(driver)
    edit_team_member_page.uncheck_folder_permission_checkbox(folder_names[1])
    edit_team_member_page.click_save()

    # check if permissions saved correctly
    dashboard_page.click_team_members_link()
    team_members_page.click_edit_team_member(config['service']['email_auth_account'])
    assert not edit_team_member_page.is_checkbox_checked(folder_names[1])
    # log out
    dashboard_page.sign_out()
    # log in as that colleague
    sign_in_email_auth(driver)
    # go to Templates
    dashboard_page.go_to_dashboard_for_service(config['service']['id'])
    dashboard_page.click_templates()
    # click through, see that child folder invisible
    show_templates_page.click_template_by_link_text(folder_names[0])
    child_folder = show_templates_page.get_folder_by_name(folder_names[1])
    name_of_folder_with_invisible_parent = folder_names[1] + " " + folder_names[2]
    assert child_folder.text == name_of_folder_with_invisible_parent
    # grandchild folder has folder path as a name
    show_templates_page.click_template_by_link_text(name_of_folder_with_invisible_parent)
    # click grandchild folder template to see that it's there
    show_templates_page.click_template_by_link_text(folder_names[2] + "_template")
    dashboard_page.sign_out()
    # delete everything
    sign_in(driver, seeded=True)
    dashboard_page.go_to_dashboard_for_service(config['service']['id'])
    dashboard_page.click_templates()
    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_template_by_link_text(folder_names[0])

    view_folder_page = ViewFolderPage(driver)
    view_folder_page.click_template_by_link_text(folder_names[1])
    view_folder_page.click_template_by_link_text(folder_names[2])

    for folder_name in reversed(folder_names):
        view_folder_page.click_template_by_link_text(folder_name + "_template")
        template_page = EditEmailTemplatePage(driver)
        template_page.click_delete()

        view_folder_page.click_manage_folder()
        manage_folder_page = ManageFolderPage(driver)
        manage_folder_page.delete_folder()
        manage_folder_page.confirm_delete_folder()


def test_change_service_name(driver, login_seeded_user):
    new_name = "Functional Tests {}".format(uuid.uuid4())
    dashboard_page = DashboardPage(driver)
    # make sure the service is actually named what we expect
    assert dashboard_page.h2_is_service_name(config['service']['name'])
    dashboard_page.go_to_dashboard_for_service(config['service']['id'])
    dashboard_page.click_settings()
    service_settings = ServiceSettingsPage(driver)
    change_name = ChangeName(driver)
    change_name.go_to_change_service_name(config['service']['id'])
    change_name.enter_new_name(new_name)
    change_name.click_save()
    change_name.enter_password(config['service']['seeded_user']['password'])
    change_name.click_save()
    service_settings.check_service_name(new_name)

    dashboard_page.go_to_dashboard_for_service(config['service']['id'])
    assert dashboard_page.h2_is_service_name(new_name)

    # change the name back
    change_name.go_to_change_service_name(config['service']['id'])
    change_name.enter_new_name(config['service']['name'])
    change_name.click_save()
    change_name.enter_password(config['service']['seeded_user']['password'])
    change_name.click_save()
    service_settings.check_service_name(config['service']['name'])

    dashboard_page.go_to_dashboard_for_service(config['service']['id'])
    assert dashboard_page.h2_is_service_name(config['service']['name'])


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
