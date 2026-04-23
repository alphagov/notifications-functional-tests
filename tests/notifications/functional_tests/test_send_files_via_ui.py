import os
import re
import uuid

import pytest
from pypdf import PdfReader
from selenium.webdriver.common.by import By

from config import config, generate_unique_email
from tests.pages import (
    ChangeLinkTextForEmailFilePage,
    ChangeRentionPeriodForEmailFilePage,
    DocumentDownloadLandingPage,
    EmailConfirmationSettingForEmailFilePage,
    ManageEmailTemplateFilePage,
    ManageFilesForEmailTemplatePage,
    PreviewConfirmYourEmailAddressPage,
    PreviewDownloadYourFilePage,
    PreviewYouHaveAFileToDownloadPage,
    SentEmailMessagePage,
    ShowTemplatesPage,
    ViewEmailTemplatePage, AddFileToEmailTemplatePage, JobPage, SendViaCsvPreviewPage, SendFilesViaUiUploadCsvPage,
    SendViaCsvPage, SendSetSenderPage, SendEmailPreviewPage, SendOneRecipientPage,
)
from tests.test_utils import (
    get_downloaded_document,
    go_to_view_template_page,
    recordtime,
    create_email_template, go_to_templates_page, create_temp_csv,
)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_attach_a_file_to_an_email_template_and_then_remove_the_file(driver, login_seeded_user):
    # Create an email template and attach a file to it
    template_name = f"Functional Tests - upload/delete file to email template - {uuid.uuid4()}"
    content = "Hi, download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Remove the file from the template
    view_email_template_page = ViewEmailTemplatePage(driver)
    go_to_manage_file_page_from_view_email_template_page(driver, file_name)
    delete_file_from_email_template_via_manage_files_page(driver)

    # Confirm file has been removed on Preview email template page
    assert view_email_template_page.get_page_banner_text() == f"‘{file_name}’ has been removed"
    assert view_email_template_page.get_file_added_count_text() == "No files added"

    # delete template
    assert view_email_template_page.get_h1_text() == template_name
    delete_template_from_view_email_template_page(driver, template_name)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
@pytest.mark.parametrize(
    "template_name, recipient_type",
    [
        (f"Functional Tests - send one off email with file via ui", "one_recipient"),
        (f"Functional Tests - send email with file via csv", "csv_of_recipients"),
    ],
)
def test_sending_an_email_notification_with_a_file_attached(driver, login_seeded_user, template_name, recipient_type):
    # Create an email template and attach a file to it
    # The uuid cannot be added to the template name in pytest.mark.parametrize method as the various workers engaged
    # during parallelization would have different uuids in the template name and throw diff errors during the test runs
    template_name = template_name + str(uuid.uuid4())
    content = "Dear ((name)), download this file:"
    recipient_data = os.environ["FUNCTIONAL_TEST_EMAIL"]
    file_name = "attachment.pdf"
    template_id = create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # go to the individual file management page
    manage_a_file_page, manage_files_page, view_email_template_page = (
        go_to_manage_file_page_from_view_email_template_page(driver, file_name)
    )

    # change the link text
    new_link_text = "file_download_link"
    change_email_template_file_link_text(driver, manage_a_file_page, new_link_text, file_name)

    # Go to email template preview page and send the email
    go_back_to_view_email_template_page_from_manage_files_page(
        file_name, manage_a_file_page, template_name, view_email_template_page
    )

    assert new_link_text in view_email_template_page.get_email_message_body_content()
    if recipient_type == "one_recipient":
        send_email_notification_with_file_attached_to_one_recipient(driver, template_name, recipient_data)

    elif recipient_type == "csv_of_recipients":
        send_email_notification_with_file_attached_via_csv(driver, template_id, template_name, recipient_data)

    # Confirm that the email is being delivered
    send_email_confirmation_page = SentEmailMessagePage(driver)
    assert send_email_confirmation_page.get_h1_text() == "Email"
    status = send_email_confirmation_page.get_notification_status()
    # Either status pops up, depending on the state of the page during test run
    assert re.search(r"Deliver(ing|ed)", status)  # either status is possible at the point the assertion is made

    # Confirm that the file download link sent to the recipient works
    # There are smoke tests and other tests covering the process of a recipient downloading
    # a document, so the whole journey will not be covered here. we will just check that the link
    # goes to the download page and that it is not the preview landing page.
    send_email_confirmation_page.click_file_download_link(new_link_text)
    document_download_landing_page = DocumentDownloadLandingPage(driver)
    assert document_download_landing_page.get_h1_text() == "You have a file to download"
    assert len(driver.find_elements(By.CLASS_NAME, "govuk-notification-banner")) == 0  # No banner present

    # go to email template preview page and delete the template
    go_to_view_template_page(driver, template_name)
    delete_template_from_view_email_template_page(driver, template_name)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_email_template_file_management_settings(driver, login_seeded_user):
    # Create an email template and attach a file to it
    template_name = f"Functional Tests - test email file management settings- {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # go to the individual file management page
    manage_a_file_page, manage_files_page, view_email_template_page = (
        go_to_manage_file_page_from_view_email_template_page(driver, file_name)
    )

    # change the link text and confirm the change
    # change_email_template_file_link_text is used in other tests and confirms the change of the link text
    new_link_text = "file_download_link"
    change_link_text_page = change_email_template_file_link_text(driver, manage_a_file_page, new_link_text, file_name)

    # Change retention period
    new_retention_period = "50"
    retention_period_label = "Available for"
    default_retention_period_text = manage_a_file_page.get_file_setting_value(retention_period_label)
    assert default_retention_period_text == "26 weeks after sending\n        (about 6 months)"
    manage_a_file_page.click_change_file_setting(retention_period_label)
    assert change_link_text_page.get_h1_text() == "How long the file is available"
    change_retention_period = ChangeRentionPeriodForEmailFilePage(driver)
    change_retention_period.fill_in_retention_period(new_retention_period)
    change_retention_period.click_continue_button()

    # Confirm retention period change
    assert (
        manage_a_file_page.get_file_setting_value(retention_period_label)
        == f"{new_retention_period} weeks after sending\n        (about 11 months)"
    )
    assert manage_a_file_page.get_h1_text() == file_name

    # Change email confirmation
    email_confirmation_label = "Ask recipient for email address"
    new_confirmation_label_choice = "No"
    confirmation_label_choice = manage_a_file_page.get_file_setting_value(email_confirmation_label)
    assert confirmation_label_choice == "Yes"
    manage_a_file_page.click_change_file_setting(email_confirmation_label)
    email_confirmation_page = EmailConfirmationSettingForEmailFilePage(driver)
    assert email_confirmation_page.get_h1_text() == "Ask recipient for their email address"
    email_confirmation_page.select_email_confirmation_option(new_confirmation_label_choice)
    email_confirmation_page.click_continue_button()

    # Confirm email confirmation option change
    assert manage_a_file_page.get_h1_text() == file_name
    assert manage_a_file_page.get_file_setting_value(email_confirmation_label) == new_confirmation_label_choice

    # Go to templates page and delete the template which would also delete file
    go_to_view_template_page(driver, template_name)
    delete_template_from_view_email_template_page(driver, template_name)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_send_file_via_ui_preview_pages(driver, login_seeded_user, download_directory):
    # Create an email template and attach a file to it
    template_name = f"Functional Tests - test email template file preview pages - {uuid.uuid4()}"
    content = "Dear ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # go to the individual file management page
    manage_a_file_page, manage_files_page, view_email_template_page = (
        go_to_manage_file_page_from_view_email_template_page(driver, file_name)
    )

    # change the link text
    new_link_text = "file_download_link"
    change_email_template_file_link_text(driver, manage_a_file_page, new_link_text, file_name)

    go_back_to_view_email_template_page_from_manage_files_page(
        file_name, manage_a_file_page, template_name, view_email_template_page
    )
    view_email_template_page.click_file_link_text(new_link_text)

    # Test you have a file to download preview page
    preview_you_have_a_file_page = PreviewYouHaveAFileToDownloadPage(driver)
    banner_title = "Preview"
    banner_heading = "This is a preview of the page your recipients will see"
    assert preview_you_have_a_file_page.get_banner_title() == banner_title
    assert preview_you_have_a_file_page.get_banner_heading() == banner_heading
    assert preview_you_have_a_file_page.get_h1_text() == "You have a file to download"
    preview_you_have_a_file_page.click_continue_button()

    # Test confirm your email address preview page
    preview_confirm_email_page = PreviewConfirmYourEmailAddressPage(driver)
    banner_title = "Preview"
    banner_heading = "This is a preview of the page your recipients will see"
    assert preview_confirm_email_page.get_banner_title() == banner_title
    assert preview_confirm_email_page.get_banner_heading() == banner_heading
    assert preview_confirm_email_page.get_h1_text() == "Confirm your email address"
    # We need the seeded user email address generated for the test run
    seeded_user_email = generate_unique_email(
        config["service"]["seeded_user"]["email"], "test_send_file_via_ui_preview_pages"
    )
    preview_confirm_email_page.fill_in_email_address(seeded_user_email)
    preview_confirm_email_page.click_continue_button()

    # Test the download your file preview page
    preview_download_file_page = PreviewDownloadYourFilePage(driver)
    banner_title = "Preview"
    banner_heading = "This is a preview of the page your recipients will see"
    assert preview_download_file_page.get_banner_title() == banner_title
    assert preview_download_file_page.get_banner_heading() == banner_heading
    assert preview_download_file_page.get_h1_text() == "Download your file"

    # Download the file and confirm the file has been downloaded
    preview_download_file_page.click_download_link()

    document_path = get_downloaded_document(download_directory, file_name)
    pdf_reader = PdfReader(document_path)
    pdf_text = pdf_reader.pages[0].extract_text()
    result_text = " ".join(pdf_text).split()
    expected_text = " ".join("This is an attachment").split()
    assert result_text == expected_text

    # go to email template preview page and delete the template
    go_to_view_template_page(driver, template_name)
    delete_template_from_view_email_template_page(driver, template_name)


# Send file via ui tests helper methods to keep things DRY
def go_to_manage_file_page_from_view_email_template_page(driver, file_name):
    view_email_template_page = ViewEmailTemplatePage(driver)
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"
    manage_files_page.click_manage_link(file_name)
    manage_a_file_page = ManageEmailTemplateFilePage(driver)
    assert manage_a_file_page.get_h1_text() == file_name
    return manage_a_file_page, manage_files_page, view_email_template_page


def change_email_template_file_link_text(driver, manage_a_file_page, new_link_text, file_name):
    link_text_label = "Link text"
    default_link_text = manage_a_file_page.get_file_setting_value(link_text_label)
    assert default_link_text == "Not set"
    manage_a_file_page.click_change_file_setting(link_text_label)
    change_link_text_page = ChangeLinkTextForEmailFilePage(driver)
    assert change_link_text_page.get_h1_text() == "Add link text"
    change_link_text_page.fill_in_link_text(new_link_text)
    change_link_text_page.click_continue_button()
    # confirm link text change
    assert manage_a_file_page.get_h1_text() == file_name
    assert manage_a_file_page.get_file_setting_value(link_text_label) == new_link_text
    return change_link_text_page


def go_back_to_view_email_template_page_from_manage_files_page(
    file_name, manage_a_file_page, template_name, view_email_template_page
):
    assert manage_a_file_page.get_h1_text() == file_name
    manage_a_file_page.click_back_link()
    assert manage_a_file_page.get_h1_text() == "Manage files"
    manage_a_file_page.click_back_link()
    assert view_email_template_page.get_h1_text() == template_name


def delete_template_from_view_email_template_page(driver, template_name):
    view_email_template_page = ViewEmailTemplatePage(driver)
    view_email_template_page.click_delete_template_link()
    view_email_template_page.click_template_deletion_confirmation_button()

    # confirm template has been deleted
    templates_page = ShowTemplatesPage(driver)
    assert templates_page.get_h1_text() == "Templates"
    assert template_name not in templates_page.get_all_listed_templates()


def delete_file_from_email_template_via_manage_files_page(driver):
    manage_a_file_page = ManageEmailTemplateFilePage(driver)
    manage_a_file_page.click_remove_file_link()
    manage_a_file_page.click_remove_file_dialog_button()


def send_email_notification_with_file_attached_to_one_recipient(driver, template_name, recipient_data):
    view_email_template_page = ViewEmailTemplatePage(driver)
    view_email_template_page.click_send()
    set_sender_page = SendSetSenderPage(driver)
    set_sender_page.wait_until_current()
    assert set_sender_page.get_h1_text() == "Where should replies come back to?"
    set_sender_page.choose_alternative_sender()
    set_sender_page.click_continue_button()
    send_to_one_recipient_page = SendOneRecipientPage(driver)
    assert send_to_one_recipient_page.get_h1_text() == f"Send ‘{template_name}’"
    send_to_one_recipient_page.send_to_myself("email")
    assert send_to_one_recipient_page.get_h1_text() == "Personalise this message"
    placeholder_value = "Esteemed Person"
    send_to_one_recipient_page.enter_placeholder_value(placeholder_value)
    assert send_to_one_recipient_page.get_placeholder_value() == placeholder_value
    send_to_one_recipient_page.click_continue()
    preview_send_one_recepient_page = SendEmailPreviewPage(driver)
    assert preview_send_one_recepient_page.get_h1_text() == f"Preview of ‘{template_name}’"
    preview_send_one_recepient_page.click_send_button()


def send_email_notification_with_file_attached_via_csv(driver, template_id, template_name, recipient_data):
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    view_email_template_page.click_send()
    set_sender_page = SendSetSenderPage(driver)
    set_sender_page.wait_until_current()
    assert set_sender_page.get_h1_text() == "Where should replies come back to?"
    set_sender_page.click_continue_button()
    send_via_csv_page = SendViaCsvPage(driver)
    assert send_via_csv_page.get_h1_text() == f"Send ‘{template_name}’"
    # Create a temp csv for this test
    send_via_csv_page.go_to_upload_csv_for_service_and_template(config["service"]["id"], template_id)
    upload_csv_page = SendFilesViaUiUploadCsvPage(driver)
    assert send_via_csv_page.get_h1_text() == "Upload a list of email addresses"
    seeded_user_email = generate_unique_email(
        config["service"]["seeded_user"]["email"], "test_send_file_via_ui_preview_pages"
    )
    _, directory, csv_filename = create_temp_csv(
        {"email address": seeded_user_email, "name": recipient_data}, include_build_id=True
    )
    upload_csv_page.upload_csv(directory, csv_filename)
    send_via_csv_preview_page = SendViaCsvPreviewPage(send_via_csv_page.driver)
    assert send_via_csv_preview_page.get_h1_text() == f"Preview of {template_name}"
    send_via_csv_preview_page.click_send()
    job_page = JobPage(driver)
    assert job_page.get_h1_text() == f"{csv_filename}"
    job_page.go_to_notification_page()


def create_an_email_template_and_attach_a_file(driver, file_name, template_name, content):
    go_to_templates_page(driver)
    template_id = create_email_template(driver, name=template_name, content=content, has_unsubscribe_link=True)
    add_file_to_email_template(driver, file_name, template_name)
    return template_id


def add_file_to_email_template(driver, file_name, template_name):
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    view_email_template_page.click_attach_files_button()
    add_file_to_email_template_page = AddFileToEmailTemplatePage(driver)
    assert add_file_to_email_template_page.get_h1_text() == "Add a file"
    add_a_file_page = AddFileToEmailTemplatePage(driver)
    assert add_a_file_page.visible_choose_file_button().is_displayed()
    file_path = f"tests/test_files/{file_name}"
    os_file_path = os.path.join(os.getcwd(), file_path)
    add_a_file_page.upload_file(os_file_path)
    manage_a_file_page = ManageEmailTemplateFilePage(driver)
    assert manage_a_file_page.get_h1_text() == file_name
    manage_a_file_page.click_add_to_template()
    # Confirm file has been attached to template on the Preview email template page
    assert_file_has_been_attached_to_email_template(driver, template_name)


def assert_file_has_been_attached_to_email_template(driver, template_name):
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    assert view_email_template_page.get_file_added_count_text() == "1 file added"

