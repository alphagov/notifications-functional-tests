import base64
import os
import urllib
import uuid
from io import BytesIO

import pytest
from pypdf import PdfReader
from retry.api import retry_call
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from config import config
from tests.decorators import retry_on_stale_element_exception
from tests.functional.preview_and_dev.consts import (
    correct_letter,
    pdf_with_virus,
    preview_error,
)
from tests.pages import (
    ApiIntegrationPage,
    ChangeLetterLanguagePage,
    DashboardPage,
    EditEmailTemplatePage,
    EditLetterTemplatePage,
    InviteUserPage,
    ManageFolderPage,
    PreviewLetterPage,
    SendLetterPreviewPage,
    ShowTemplatesPage,
    TeamMembersPage,
    UploadCsvPage,
    ViewFolderPage,
    ViewLetterTemplatePage,
)
from tests.pages.rollups import get_mobile_number, sign_in, sign_in_email_auth
from tests.postman import (
    get_notification_by_id_via_api,
    get_pdf_for_letter_via_api,
    send_notification_via_csv,
    send_precompiled_letter_via_api,
)
from tests.test_utils import (
    NotificationStatuses,
    add_letter_attachment_for_template,
    assert_notification_body,
    create_email_template,
    create_letter_template,
    create_sms_template,
    delete_letter_attachment,
    delete_template,
    edit_email_template,
    edit_sms_template,
    get_downloaded_document,
    go_to_templates_page,
    manage_letter_attachment,
    pdf_page_has_text,
    recordtime,
    send_bilingual_letter_to_one_recipient,
    send_letter_to_one_recipient,
    send_notification_to_one_recipient,
)


@recordtime
@pytest.mark.parametrize(
    "message_type",
    ["sms", "email", pytest.param("letter", marks=pytest.mark.template_preview)],
)
def test_send_csv(driver, login_seeded_user, client_live_key, client_test_key, message_type):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])

    template_id = {
        "email": config["service"]["templates"]["email"],
        "sms": config["service"]["templates"]["sms"],
        "letter": config["service"]["templates"]["letter"],
    }.get(message_type)

    dashboard_stats_before = get_dashboard_stats(dashboard_page, message_type, template_id)

    upload_csv_page = UploadCsvPage(driver)
    notification_id = send_notification_via_csv(upload_csv_page, message_type, seeded=True)

    notification = retry_call(
        get_notification_by_id_via_api,
        fargs=[
            client_test_key if message_type == "letter" else client_live_key,
            notification_id,
            NotificationStatuses.ACCEPTED if message_type == "letter" else NotificationStatuses.SENT,
        ],
        tries=config["notification_retry_times"],
        delay=config["notification_retry_interval"],
    )
    assert_notification_body(notification_id, notification)

    # test the whole letter creation flow, by checking the PDF has been created
    if message_type == "letter":
        retry_call(
            get_pdf_for_letter_via_api,
            fargs=[client_live_key, notification_id],
            tries=config["notification_retry_times"],
            delay=config["notification_retry_interval"],
        )

    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])

    dashboard_stats_after = get_dashboard_stats(dashboard_page, message_type, template_id)

    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)


@recordtime
def test_edit_and_delete_email_template(driver, login_seeded_user, client_live_key):
    template_name = f"edit/delete email template test {uuid.uuid4()}"
    go_to_templates_page(driver)

    create_email_template(driver, name=template_name, content=None)
    go_to_templates_page(driver)
    current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]
    assert template_name in current_templates

    new_template_name = f"{template_name} v2"
    edit_email_template(
        driver,
        template_name=template_name,
        new_template_name=new_template_name,
        subject="my new email subject",
        content="my new template content. Job id: ((build_id))",
    )

    go_to_templates_page(driver)
    current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]

    assert template_name not in current_templates
    assert new_template_name in current_templates

    delete_template(driver, template_name)
    current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]

    assert template_name not in current_templates
    assert new_template_name not in current_templates


@recordtime
def test_edit_and_delete_sms_template(driver, login_seeded_user, client_live_key):
    template_name = f"edit/delete sms template test {uuid.uuid4()}"
    go_to_templates_page(driver)

    create_sms_template(driver, name=template_name, content=None)
    go_to_templates_page(driver)
    current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]

    assert template_name in current_templates

    new_template_name = f"{template_name} v2"
    edit_sms_template(
        driver,
        template_name=template_name,
        new_template_name=new_template_name,
        content="my new template content. Job id: ((build_id))",
    )

    go_to_templates_page(driver)
    current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]

    assert template_name not in current_templates
    assert new_template_name in current_templates

    delete_template(driver, new_template_name)
    current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]

    assert template_name not in current_templates
    assert new_template_name not in current_templates


@recordtime
def test_edit_and_delete_letter_template(driver, login_seeded_user, client_live_key):
    template_name = f"edit/delete letter template test {uuid.uuid4()}"
    go_to_templates_page(driver)

    create_letter_template(driver, name=template_name, content=None)
    go_to_templates_page(driver)
    current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]

    assert template_name in current_templates

    delete_template(driver, template_name)
    current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]

    assert template_name not in current_templates


@recordtime
def test_send_bilingual_letter(driver, login_seeded_user, client_live_key, download_directory):
    template_name = f"send bilingual letter template test {uuid.uuid4()}"
    go_to_templates_page(driver)

    create_letter_template(driver, name=template_name, content=None)

    assert len(driver.find_elements("css selector", ".letter")) == 1, "There should only be a single (English) page"

    view_template_page = ViewLetterTemplatePage(driver)
    view_template_page.click_change_language()

    change_language_page = ChangeLetterLanguagePage(driver)
    change_language_page.change_language("welsh_then_english")
    change_language_page.click_save()

    assert len(driver.find_elements("css selector", ".letter")) == 2, (
        "The letter should have two pages - Welsh then English"
    )

    view_template_page.click_edit_welsh_body()

    edit_template_page = EditLetterTemplatePage(driver)
    edit_template_page.template_content_input = "My Welsh body ((welsh_var))"
    edit_template_page.click_save()
    edit_template_page.click_save()  # Confirm 'breaking' template change.

    view_template_page.click_edit_english_body()

    edit_template_page = EditLetterTemplatePage(driver)
    edit_template_page.template_content_input = "My English body ((english_var))"
    edit_template_page.click_save()
    edit_template_page.click_save()  # Confirm 'breaking' template change.

    placeholders = {
        "welsh_var": "Mae pwy bynnag a ysgrifennodd y prawf hwn yn berson gwych",
        "english_var": "Some boring placeholder text for a normal letter.",
    }
    send_bilingual_letter_to_one_recipient(
        driver,
        template_name,
        address="notify developer\nTest street\nSW1 1AA",
        placeholders=placeholders,
    )

    send_letter_preview_page = SendLetterPreviewPage(driver)
    filename = send_letter_preview_page.click_download_pdf_link()

    letter_pdf = get_downloaded_document(download_directory, filename)
    pdf = PdfReader(letter_pdf)

    assert pdf_page_has_text(pdf.pages[0], placeholders["welsh_var"]), "Couldn't find Welsh placeholder on first page"
    assert pdf_page_has_text(pdf.pages[1], placeholders["english_var"]), (
        "Couldn't find English placeholder on first page"
    )

    change_language_page.click_templates()
    delete_template(driver, template_name)
    current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]

    assert template_name not in current_templates


@recordtime
def test_add_letter_attachment_then_send_letter_then_delete_attachment(driver, login_seeded_user, client_live_key):
    test_id = uuid.uuid4()
    template_name = f"edit/delete letter attachment test {test_id}"
    go_to_templates_page(driver)
    create_letter_template(driver, name=template_name, content=None)
    go_to_templates_page(driver)
    add_letter_attachment_for_template(driver, name=template_name)
    assert driver.find_element(By.CLASS_NAME, "edit-template-link-attachment").text == "Manage attachment"

    send_letter_to_one_recipient(
        driver, template_name, address=f"{test_id}\nTest street\nSW1 1AA", build_id=str(test_id)
    )

    letter_preview_page = PreviewLetterPage(driver)
    notification_id = letter_preview_page.get_notification_id()

    # wait until notification is in ACCEPTED state
    retry_call(
        get_notification_by_id_via_api,
        fargs=[
            client_live_key,
            notification_id,
            NotificationStatuses.ACCEPTED,
        ],
        tries=config["notification_retry_times"],
        delay=config["notification_retry_interval"],
    )

    # wait until the PDF for the letter is generated
    letter_pdf = retry_call(
        get_pdf_for_letter_via_api,
        fargs=[client_live_key, notification_id],
        tries=config["pdf_generation_retry_times"],
        delay=config["pdf_generation_retry_interval"],
    )

    pdf_reader = PdfReader(letter_pdf)
    assert len(pdf_reader.pages) == 2
    attachment_page = pdf_reader.pages[1]
    assert "This is an attachment" in attachment_page.extract_text()

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config["service"]["id"])
    dashboard_page.click_templates()
    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_template_by_link_text(template_name)

    manage_letter_attachment(driver)
    assert driver.find_element(By.TAG_NAME, "h1").text == "attachment.pdf"

    delete_letter_attachment(driver)
    go_to_templates_page(driver)
    delete_template(driver, template_name)


@recordtime
def test_send_email_with_placeholders_to_one_recipient(request, driver, client_live_key, login_seeded_user):
    test_name = request.node.name
    go_to_templates_page(driver)
    template_name = f"email with placeholders {uuid.uuid4()}"
    content = "Hi ((name)), Is ((email address)) your email address? We want to send you some ((things))"
    template_id = create_email_template(driver, name=template_name, content=content)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])
    dashboard_stats_before = get_dashboard_stats(dashboard_page, "email", template_id)

    placeholders = send_notification_to_one_recipient(
        driver,
        template_name,
        "email",
        test=False,
        recipient_data=os.environ["FUNCTIONAL_TEST_EMAIL"],
        placeholders_number=2,
    )
    assert list(placeholders[0].keys()) == ["name"]
    assert list(placeholders[1].keys()) == ["things"]

    dashboard_page.click_continue()
    notification_id = dashboard_page.get_notification_id()
    one_off_email = client_live_key.get_notification_by_id(notification_id)
    assert one_off_email.get("created_by_name") == f"Preview admin tests user - {test_name}"

    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])
    dashboard_stats_after = get_dashboard_stats(dashboard_page, "email", template_id)
    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)

    placeholders_test = send_notification_to_one_recipient(
        driver, template_name, "email", test=True, placeholders_number=2, test_name=test_name
    )
    assert list(placeholders_test[0].keys()) == ["name"]
    assert list(placeholders_test[1].keys()) == ["things"]

    delete_template(driver, template_name)


@recordtime
def test_send_sms_with_placeholders_to_one_recipient(driver, client_live_key, login_seeded_user):
    go_to_templates_page(driver)
    template_name = f"sms with placeholders {uuid.uuid4()}"
    content = "Hi ((name)), Is ((phone number)) your mobile number? We want to send you some ((things))"
    template_id = create_sms_template(driver, name=template_name, content=content)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])
    dashboard_stats_before = get_dashboard_stats(dashboard_page, "sms", template_id)

    placeholders = send_notification_to_one_recipient(
        driver, template_name, "sms", test=False, recipient_data=os.environ["TEST_NUMBER"], placeholders_number=2
    )
    assert list(placeholders[0].keys()) == ["name"]
    assert list(placeholders[1].keys()) == ["things"]

    dashboard_page.click_continue()
    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])
    dashboard_stats_after = get_dashboard_stats(dashboard_page, "sms", template_id)
    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)

    # Test sending to ourselves (seeded user)
    placeholders_test = send_notification_to_one_recipient(
        driver,
        template_name,
        "sms",
        test=True,
        recipient_data=get_mobile_number(
            account_type="seeded", test_name="test_send_sms_with_placeholders_to_one_recipient"
        ),
        placeholders_number=2,
    )
    assert list(placeholders_test[0].keys()) == ["name"]
    assert list(placeholders_test[1].keys()) == ["things"]

    delete_template(driver, template_name)


@pytest.mark.template_preview
def test_view_precompiled_letter_message_log_delivered(driver, login_seeded_user, client_test_key):
    reference = f"functional_tests_precompiled_{uuid.uuid4()}_delivered"

    notification_id = send_precompiled_letter_via_api(
        reference,
        client_test_key,
        BytesIO(base64.b64decode(correct_letter)),
    )

    api_integration_page = ApiIntegrationPage(driver)

    retry_call(
        _check_status_of_notification,
        fargs=[api_integration_page, config["service"]["id"], reference, "received"],
        tries=config["notification_retry_times"],
        delay=config["notification_retry_interval"],
    )

    ref_link = config["notify_admin_url"] + "/services/" + config["service"]["id"] + "/notification/" + notification_id
    link = api_integration_page.get_view_letter_link(reference)
    assert link == ref_link


@pytest.mark.template_preview
def test_view_precompiled_letter_preview_delivered(driver, login_seeded_user, client_test_key):
    reference = f"functional_tests_precompiled_letter_preview_{uuid.uuid4()}_delivered"

    notification_id = send_precompiled_letter_via_api(
        reference,
        client_test_key,
        BytesIO(base64.b64decode(correct_letter)),
    )

    api_integration_page = ApiIntegrationPage(driver)

    retry_call(
        _check_status_of_notification,
        fargs=[api_integration_page, config["service"]["id"], reference, "received"],
        tries=config["notification_retry_times"],
        delay=config["notification_retry_interval"],
    )

    api_integration_page.go_to_preview_letter(reference)

    letter_preview_page = PreviewLetterPage(driver)
    assert letter_preview_page.is_text_present_on_page("Provided as PDF")

    # Check the pdf link looks valid
    pdf_download_link = letter_preview_page.get_download_pdf_link()

    link = (
        config["notify_admin_url"]
        + "/services/"
        + config["service"]["id"]
        + "/notification/"
        + notification_id
        + ".pdf"
    )

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


@pytest.mark.antivirus
def test_view_precompiled_letter_message_log_virus_scan_failed(driver, login_seeded_user, client_test_key):
    reference = "functional_tests_precompiled_" + str(uuid.uuid1()) + "_virus_scan_failed"

    send_precompiled_letter_via_api(
        reference,
        client_test_key,
        BytesIO(base64.b64decode(pdf_with_virus)),
    )

    api_integration_page = ApiIntegrationPage(driver)

    retry_call(
        _check_status_of_notification,
        fargs=[
            api_integration_page,
            config["service"]["id"],
            reference,
            NotificationStatuses.VIRUS_SCAN_FAILED,
        ],
        tries=config["notification_retry_times"],
        delay=config["notification_retry_interval"],
    )

    assert api_integration_page.get_view_letter_link(reference) is None


@pytest.mark.xdist_group(name="template-folders")
def test_creating_moving_and_deleting_template_folders(driver, login_seeded_user):
    # create new template
    template_name = f"template-for-folder-test {uuid.uuid4()}"
    folder_name = f"test-folder {uuid.uuid4()}"

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config["service"]["id"])
    dashboard_page.click_templates()

    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_add_new_template()
    show_templates_page.select_email()

    edit_template_page = EditEmailTemplatePage(driver)
    edit_template_page.fill_template(name=template_name)
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
    new_folder_name = folder_name + "-new"
    manage_folder_page.set_name(new_folder_name)
    view_folder_page.assert_name_equals(new_folder_name)

    # try to delete folder
    view_folder_page.click_manage_folder()
    manage_folder_page.delete_folder()  # fails due to not being empty

    # check error message visible
    assert manage_folder_page.get_errors() == "You must empty this folder before you can delete it"

    # move template out of folder
    view_folder_page.select_template_checkbox(template_id)
    view_folder_page.move_to_root_template_folder()

    # delete folder
    view_folder_page.click_manage_folder()
    manage_folder_page.delete_folder()
    manage_folder_page.confirm_delete_folder()
    current_folders = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]
    if len(current_folders) == 0:
        current_folders = [x.text for x in driver.find_elements(By.CLASS_NAME, "message-name")]
    # assert folder not visible
    assert new_folder_name not in current_folders

    # delete template
    show_templates_page.click_template_by_link_text(template_name)
    edit_template_page.click_delete()

    assert template_name not in [x.text for x in driver.find_elements(By.CLASS_NAME, "message-name")]


@pytest.mark.xdist_group(name="template-folders")
def test_template_folder_permissions(driver, request, login_seeded_user):
    family_id = uuid.uuid4()
    folder_names = [
        f"test-parent-folder {family_id}",
        f"test-child-folder {family_id}",
        f"test-grandchild-folder {family_id}",
    ]
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config["service"]["id"])
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
        edit_template_page.fill_template(name=(folder_name + "_template"))
        # go back to view folder page
        edit_template_page.click_folder_path(folder_name)

    # go to Team members page
    dashboard_page.click_team_members_link()
    team_members_page = TeamMembersPage(driver)
    # edit colleague's permissions so child folder is invisible
    team_members_page.click_edit_team_member(config["service"]["email_auth_account"])
    edit_team_member_page = InviteUserPage(driver)
    edit_team_member_page.uncheck_folder_permission_checkbox(folder_names[1])
    edit_team_member_page.click_save()

    # check if permissions saved correctly
    dashboard_page.click_team_members_link()
    team_members_page.click_edit_team_member(config["service"]["email_auth_account"])
    assert not edit_team_member_page.is_checkbox_checked(folder_names[1])
    # log out
    dashboard_page.sign_out()
    # log in as that colleague
    sign_in_email_auth(driver)
    # go to Templates
    dashboard_page.go_to_dashboard_for_service(config["service"]["id"])
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
    sign_in(driver, account_type="seeded", test_name=request.node.name)
    dashboard_page.go_to_dashboard_for_service(config["service"]["id"])
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


def _check_status_of_notification(page, functional_tests_service_id, reference_to_check, status_to_check):
    page.go_to_api_integration_for_service(service_id=functional_tests_service_id)
    page.expand_all_messages()
    notification_offset = page.find_notification_offset_for_client_reference(reference_to_check)
    assert status_to_check == page.get_notification_status_for_log_offset(notification_offset)


@retry_on_stale_element_exception
def get_dashboard_stats(dashboard_page, message_type, template_id):
    return {
        "total_messages_sent": dashboard_page.get_total_message_count(message_type),
        "template_messages_sent": _get_template_count(dashboard_page, template_id),
    }


def assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after):
    for k in dashboard_stats_before.keys():
        assert dashboard_stats_after[k] > dashboard_stats_before[k]


def _get_template_count(dashboard_page, template_id):
    try:
        template_messages_count = dashboard_page.get_template_message_count(template_id)
    except TimeoutException:
        return 0  # template count may not exist yet if no messages sent
    else:
        return template_messages_count
