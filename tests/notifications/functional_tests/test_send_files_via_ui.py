import os
import uuid

import pytest
from pypdf import PdfReader
from selenium.webdriver.common.by import By

from config import config, generate_unique_email
from tests.pages import (
    AddFileToEmailTemplatePage,
    ChangeLinkTextForEmailFilePage,
    ChangeRentionPeriodForEmailFilePage,
    DocumentDownloadLandingPage,
    EmailConfirmationSettingForEmailFilePage,
    JobPage,
    ManageEmailTemplateFilePage,
    ManageFilesForEmailTemplatePage,
    PreviewConfirmYourEmailAddressPage,
    PreviewDownloadYourFilePage,
    PreviewYouHaveAFileToDownloadPage,
    SendEmailPreviewPage,
    SendFilesViaUiUploadCsvPage,
    SendOneRecipientPage,
    SendSetSenderPage,
    SendViaCsvPage,
    SendViaCsvPreviewPage,
    SentEmailMessagePage,
    ShowTemplatesPage,
    ViewEmailTemplatePage,
)
from tests.test_utils import (
    create_email_template,
    create_temp_csv,
    delete_file_from_email_template_via_manage_files_page,
    get_downloaded_document,
    go_to_email_template_preview_page_from_a_document_download_pages,
    go_to_templates_page,
    recordtime,
)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_attaching_a_file_to_an_email_template_and_also_removing_the_file(driver, login_seeded_user):
    # Creat an email template and attach a file to it
    template_name = f"Functional Tests - upload/delete file to email template - {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    assert_file_has_been_attached_to_email_template(driver, template_name)

    # Remove the file from the template
    view_email_template_page = ViewEmailTemplatePage(driver)
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"
    manage_files_page.click_manage_link(file_name)
    delete_file_from_email_template_via_manage_files_page(driver)

    # Confirm file has been removed on Preview email template page
    assert view_email_template_page.get_page_banner_text() == f"‘{file_name}’ has been removed"
    assert view_email_template_page.get_file_added_count_text() == "No files added"

    # delete template
    assert view_email_template_page.get_h1_text() == template_name
    delete_email_template_for_send_file_via_ui_tests(driver, view_email_template_page, template_name)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_send_one_off_email_with_file_via_ui(driver, login_seeded_user):
    # # Creat an email template and attach a file to it
    template_name = f"Functional Tests - send one off email with file via ui - {uuid.uuid4()}"
    content = "Testing sending a one off email notification. with an email file. Test file below:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    assert_file_has_been_attached_to_email_template(driver, template_name)

    # Go to the individual file management page
    view_email_template_page = ViewEmailTemplatePage(driver)
    manage_a_file_page, manage_files_page = go_to_file_management_page_from_email_template_preview(
        driver, file_name, view_email_template_page
    )

    # Change the link text
    link_text_label = "Link text"
    new_link_text = "file_download_link"
    change_email_template_file_link_text(driver, manage_a_file_page, link_text_label, new_link_text, file_name)

    # Confirm link text change
    assert manage_a_file_page.get_file_setting_value(link_text_label) == new_link_text

    # Go back to email template preview page
    go_back_to_email_template_from_file_management_page(
        file_name, manage_a_file_page, template_name, view_email_template_page
    )

    # Send the email
    assert new_link_text in view_email_template_page.get_email_message_body_content()
    send_email_notification_with_file_attached_to_one_recipient(driver, view_email_template_page, template_name)

    # Confirm that the email is being delivered
    send_email_confirmation_page = SentEmailMessagePage(driver)
    assert_email_notification_with_a_file_attached_was_sent(send_email_confirmation_page)

    # Confirm that the file download link sent to the recipient works
    # There are smoke tests and other tests covering the process of a recipient downloading
    # a document, so the whole journey will not be covered here. we will just check that the link
    # goes to the download page and that it is not the preview landing page
    assert_send_file_via_ui_file_download_links_work_as_expected(driver, new_link_text, send_email_confirmation_page)

    # Go to service templates page and select the template
    document_download_landing_page = DocumentDownloadLandingPage(driver)
    go_to_email_template_preview_page_from_a_document_download_pages(
        driver, template_name, document_download_landing_page
    )

    # Delete the template
    assert view_email_template_page.get_h1_text() == template_name
    delete_email_template_for_send_file_via_ui_tests(driver, view_email_template_page, template_name)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_email_template_file_management_settings(driver, login_seeded_user):
    # Creat an email template and attach a file to it
    template_name = f"Functional Tests - test email file management settings- {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    assert_file_has_been_attached_to_email_template(driver, template_name)

    # Go to the individual file management page
    view_email_template_page = ViewEmailTemplatePage(driver)
    manage_a_file_page, manage_files_page = go_to_file_management_page_from_email_template_preview(
        driver, file_name, view_email_template_page
    )

    # Change link text
    new_link_text = "file_download_link"
    link_text_label = "Link text"
    change_link_text_page = change_email_template_file_link_text(
        driver, manage_a_file_page, link_text_label, new_link_text, file_name
    )

    # Confirm link text change
    assert manage_a_file_page.get_file_setting_value(link_text_label) == new_link_text

    # Change retention period
    new_retention_period = "50"
    retention_period_label = "Available for"
    change_email_template_retention_period(
        change_link_text_page, driver, manage_a_file_page, new_retention_period, retention_period_label
    )

    # Confirm retention period change
    assert (
        manage_a_file_page.get_file_setting_value(retention_period_label)
        == f"{new_retention_period} weeks after sending\n        (about 11 months)"
    )
    assert manage_a_file_page.get_h1_text() == file_name

    # Change email confirmation
    email_confirmation_label = "Ask recipient for email address"
    new_confirmation_label_choice = "No"
    change_email_template_email_confirmation(
        driver, email_confirmation_label, manage_a_file_page, new_confirmation_label_choice
    )

    # Confirm email confirmation option change
    assert manage_a_file_page.get_h1_text() == file_name
    assert manage_a_file_page.get_file_setting_value(email_confirmation_label) == new_confirmation_label_choice

    # Go to templates page and delete the template which would also delete file
    go_back_to_email_template_from_file_management_page(
        file_name, manage_a_file_page, template_name, view_email_template_page
    )

    delete_email_template_for_send_file_via_ui_tests(driver, view_email_template_page, template_name)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_send_file_via_ui_preview_pages(driver, login_seeded_user, download_directory):
    # Creat an email template and attach a file to it
    template_name = f"Functional Tests - test email template file preview pages - {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    assert_file_has_been_attached_to_email_template(driver, template_name)

    # go to the individual file management page
    # go to the individual file management page
    view_email_template_page = ViewEmailTemplatePage(driver)
    manage_a_file_page, manage_files_page = go_to_file_management_page_from_email_template_preview(
        driver, file_name, view_email_template_page
    )

    # change the link text
    link_text_label = "Link text"
    new_link_text = "file_download_link"

    change_email_template_file_link_text(driver, manage_a_file_page, link_text_label, new_link_text, file_name)

    # confirm link text change
    assert manage_a_file_page.get_file_setting_value(link_text_label) == new_link_text

    # go to template page and click on file link
    go_back_to_email_template_from_file_management_page(
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

    # delete the template which will also archive the file attached
    service_templates_url = f"{config['notify_admin_url']}/services/{config['service']['id']}/templates"
    preview_download_file_page.get(service_templates_url)
    assert view_email_template_page.get_h1_text() == "Templates"
    templates_page = ShowTemplatesPage(driver)
    templates_page.click_template_by_link_text(template_name)
    assert view_email_template_page.get_h1_text() == template_name
    delete_email_template_for_send_file_via_ui_tests(driver, view_email_template_page, template_name)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_send_email_notification_with_an_email_file_via_csv(driver, login_seeded_user):
    # Creat an email template and attach a file to it
    template_name = f"Functional Tests - send email with file via csv - {uuid.uuid4()}"
    content = "Testing sending a one off email notification. with an email file. Test file below:"
    file_name = "attachment.pdf"
    template_id = create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    assert_file_has_been_attached_to_email_template(driver, template_name)

    # Go to the individual file management page
    view_email_template_page = ViewEmailTemplatePage(driver)
    manage_a_file_page, manage_files_page = go_to_file_management_page_from_email_template_preview(
        driver, file_name, view_email_template_page
    )

    # Change the link text
    link_text_label = "Link text"
    new_link_text = "file_download_link"
    change_email_template_file_link_text(driver, manage_a_file_page, link_text_label, new_link_text, file_name)

    # Confirm link text change
    assert manage_a_file_page.get_file_setting_value(link_text_label) == new_link_text

    # Go to the email template preview page
    go_back_to_email_template_from_file_management_page(
        file_name, manage_a_file_page, template_name, view_email_template_page
    )

    # Send the email
    assert new_link_text in view_email_template_page.get_email_message_body_content()
    send_email_notification_with_file_attached_via_csv(driver, template_id, template_name, view_email_template_page)

    # Confirm that the email is being delivered
    send_email_confirmation_page = SentEmailMessagePage(driver)
    assert_email_notification_with_a_file_attached_was_sent(send_email_confirmation_page)

    # Confirm that the file download link sent to the recipient works
    # There are smoke tests and other tests covering the process of a recipient downloading
    # a document, so the whole journey will not be covered here. we will just check that the link
    # goes to the download page and that it is not the preview landing page
    assert_send_file_via_ui_file_download_links_work_as_expected(driver, new_link_text, send_email_confirmation_page)

    # Go to service templates page and select the template
    document_download_landing_page = DocumentDownloadLandingPage(driver)
    go_to_email_template_preview_page_from_a_document_download_pages(
        driver, template_name, document_download_landing_page
    )

    # Delete the template
    assert view_email_template_page.get_h1_text() == template_name
    delete_email_template_for_send_file_via_ui_tests(driver, view_email_template_page, template_name)


# send file via ui tests helper methods to keep things DRY
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


def assert_file_has_been_attached_to_email_template(driver, template_name):
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    assert view_email_template_page.get_file_added_count_text() == "1 file added"


def go_to_file_management_page_from_email_template_preview(driver, file_name, view_email_template_page):
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"
    manage_files_page.click_manage_link(file_name)
    manage_a_file_page = ManageEmailTemplateFilePage(driver)
    assert manage_a_file_page.get_h1_text() == file_name
    return manage_a_file_page, manage_files_page


def change_email_template_file_link_text(driver, manage_a_file_page, link_text_label, new_link_text, file_name):
    default_link_text = manage_a_file_page.get_file_setting_value(link_text_label)
    assert default_link_text == "Not set"
    manage_a_file_page.click_change_file_setting(link_text_label)
    change_link_text_page = ChangeLinkTextForEmailFilePage(driver)
    assert change_link_text_page.get_h1_text() == "Add link text"
    change_link_text_page.fill_in_link_text(new_link_text)
    change_link_text_page.click_continue_button()
    return change_link_text_page


def change_email_template_retention_period(
    change_link_text_page, driver, manage_a_file_page, new_retention_period, retention_period_label
):
    default_retention_period_text = manage_a_file_page.get_file_setting_value(retention_period_label)
    assert default_retention_period_text == "26 weeks after sending\n        (about 6 months)"
    manage_a_file_page.click_change_file_setting(retention_period_label)
    assert change_link_text_page.get_h1_text() == "How long the file is available"
    change_retention_period = ChangeRentionPeriodForEmailFilePage(driver)
    change_retention_period.fill_in_retention_period(new_retention_period)
    change_retention_period.click_continue_button()


def change_email_template_email_confirmation(
    driver, email_confirmation_label, manage_a_file_page, new_confirmation_label_choice
):
    confirmation_label_choice = manage_a_file_page.get_file_setting_value(email_confirmation_label)
    assert confirmation_label_choice == "Yes"
    manage_a_file_page.click_change_file_setting(email_confirmation_label)
    email_confirmation_page = EmailConfirmationSettingForEmailFilePage(driver)
    assert email_confirmation_page.get_h1_text() == "Ask recipient for their email address"
    email_confirmation_page.select_email_confirmation_option(new_confirmation_label_choice)
    email_confirmation_page.click_continue_button()


def go_back_to_email_template_from_file_management_page(
    file_name, manage_a_file_page, template_name, view_email_template_page
):
    assert manage_a_file_page.get_h1_text() == file_name
    manage_a_file_page.click_back_link()
    assert manage_a_file_page.get_h1_text() == "Manage files"
    manage_a_file_page.click_back_link()
    assert view_email_template_page.get_h1_text() == template_name


def send_email_notification_with_file_attached_to_one_recipient(driver, view_email_template_page, template_name):
    view_email_template_page.click_send()
    set_sender_page = SendSetSenderPage(driver)
    set_sender_page.wait_until_current()
    assert set_sender_page.get_h1_text() == "Where should replies come back to?"
    set_sender_page.click_continue_button()
    send_to_one_recipient_page = SendOneRecipientPage(driver)
    assert send_to_one_recipient_page.get_h1_text() == f"Send ‘{template_name}’"
    send_to_one_recipient_page.send_to_myself("email")
    preview_send_one_recepient_page = SendEmailPreviewPage(driver)
    assert preview_send_one_recepient_page.get_h1_text() == f"Preview of ‘{template_name}’"
    preview_send_one_recepient_page.click_send_button()


def delete_email_template_for_send_file_via_ui_tests(driver, view_email_template_page, template_name):
    view_email_template_page.click_delete_template_link()
    view_email_template_page.click_template_deletion_confirmation_button()

    # confirm template has been deleted
    templates_page = ShowTemplatesPage(driver)
    assert templates_page.get_h1_text() == "Templates"
    assert template_name not in templates_page.get_all_listed_templates()


def assert_email_notification_with_a_file_attached_was_sent(send_email_confirmation_page):
    assert send_email_confirmation_page.get_h1_text() == "Email"
    status = send_email_confirmation_page.get_notification_status()
    assert (
        "Delivering" in status or "Delivered"
    )  # Either status pops up, depending on the state of the page during test run
    return send_email_confirmation_page


def assert_send_file_via_ui_file_download_links_work_as_expected(driver, new_link_text, send_email_confirmation_page):
    send_email_confirmation_page.click_file_download_link(new_link_text)
    document_download_landing_page = DocumentDownloadLandingPage(driver)
    assert document_download_landing_page.get_h1_text() == "You have a file to download"
    assert len(driver.find_elements(By.CLASS_NAME, "govuk-notification-banner")) == 0  # No banner present
    return document_download_landing_page


def send_email_notification_with_file_attached_via_csv(driver, template_id, template_name, view_email_template_page):
    assert view_email_template_page.get_h1_text() == template_name
    view_email_template_page.click_send()
    set_sender_page = SendSetSenderPage(driver)
    set_sender_page.wait_until_current()
    assert set_sender_page.get_h1_text() == "Where should replies come back to?"
    set_sender_page.click_continue_button()
    send_via_csv_page = SendViaCsvPage(driver)
    assert send_via_csv_page.get_h1_text() == f"Send ‘{template_name}’"
    # Create temp csv for this test
    send_via_csv_page.go_to_upload_csv_for_service_and_template(config["service"]["id"], template_id)
    upload_csv_page = SendFilesViaUiUploadCsvPage(driver)
    assert send_via_csv_page.get_h1_text() == "Upload a list of email addresses"
    seeded_user_email = generate_unique_email(
        config["service"]["seeded_user"]["email"], "test_send_file_via_ui_preview_pages"
    )
    _, directory, csv_filename = create_temp_csv({"email address": seeded_user_email}, include_build_id=True)
    upload_csv_page.upload_csv(directory, csv_filename)
    send_via_csv_preview_page = SendViaCsvPreviewPage(send_via_csv_page.driver)
    assert send_via_csv_preview_page.get_h1_text() == f"Preview of {template_name}"
    send_via_csv_preview_page.click_send()
    job_page = JobPage(driver)
    assert job_page.get_h1_text() == f"{csv_filename}"
    job_page.go_to_notification_page()
