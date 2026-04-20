import uuid

import pytest

from config import config
from pypdf import PdfReader

from config import config, generate_unique_email
from tests.pages import (
    ChangeLinkTextForEmailFilePage,
    ChangeRentionPeriodForEmailFilePage,
    DocumentDownloadLandingPage,
    EmailConfirmationSettingForEmailFilePage,
    ManageEmailTemplateFilePage,
    ManageFilesForEmailTemplatePage,
    SendEmailPreviewPage,
    SendOneRecipientPage,
    SendSetSenderPage,
    SentEmailMessagePage,
    PreviewConfirmYourEmailAddressPage,
    PreviewDownloadYourFilePage,
    PreviewYouHaveAFileToDownloadPage,
    ShowTemplatesPage,
    ViewEmailTemplatePage, SendViaCsvPage, SendViaCsvPreviewPage, JobPage,
)
from tests.postman import send_notification_via_csv
from tests.test_utils import (
    create_an_email_template_and_attach_a_file,
    delete_file_from_email_template_via_manage_files_page,
    get_downloaded_document,
    recordtime, create_temp_csv,
)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_attaching_files_to_emails_and_also_deleting_them_via_ui(driver, login_seeded_user):
    # Test Creating an email template and attach a file to it
    template_name = f"Functional Tests - upload/delete file to email template - {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    assert view_email_template_page.get_file_added_count_text() == "1 file added"

    # Test removing the file from the template
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
    # Create an email template
    template_name = f"Functional Tests - send one off email with file via ui - {uuid.uuid4()}"
    content = "Testing sending a one off email notification. with an email file. Test file below:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    assert view_email_template_page.get_file_added_count_text() == "1 file added"

    # go to the individual file management page and change the link text
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"
    link_text_label = "Link text"
    link_text = "file_download_link"
    manage_files_page.click_manage_link(file_name)
    manage_file_page = ManageEmailTemplateFilePage(driver)
    assert manage_file_page.get_h1_text() == file_name
    manage_file_page.click_change_file_setting(link_text_label)
    change_link_text_page = ChangeLinkTextForEmailFilePage(driver)
    assert change_link_text_page.get_h1_text() == "Add link text"
    change_link_text_page.fill_in_link_text(link_text)
    change_link_text_page.click_continue_button()

    manage_file_page.click_back_link()
    assert manage_file_page.get_h1_text() == "Manage files"
    manage_file_page.click_back_link()

    # send the email
    assert view_email_template_page.get_h1_text() == template_name
    assert link_text in view_email_template_page.get_email_message_body_content()
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

    # confirm that the email is being delivered
    send_email_confirmation_page = SentEmailMessagePage(driver)
    assert send_email_confirmation_page.get_h1_text() == "Email"
    assert "Delivering" in send_email_confirmation_page.get_notification_status()

    # Confirm that the file download link sent to the recipient works
    # There are smoke tests and other tests covering the process of a recipient downloading
    # a document, so the whole journey will not be covered here
    send_email_confirmation_page.click_file_download_link(link_text)
    you_have_a_file_to_download_page = DocumentDownloadLandingPage(driver)
    assert you_have_a_file_to_download_page.get_h1_text() == "You have a file to download"
    you_have_a_file_to_download_page.go_to_download_page()

    # Go to service templates page and select the template
    base_url = config["notify_admin_url"]
    service_template_page_url = f"{base_url}/services/{config['service']['id']}/templates"
    you_have_a_file_to_download_page.get(service_template_page_url)
    templates_pages = ShowTemplatesPage(driver)
    assert templates_pages.get_h1_text() == "Templates"
    templates_pages.click_template_by_link_text(template_name)

    # delete the template
    assert view_email_template_page.get_h1_text() == template_name
    delete_email_template_for_send_file_via_ui_tests(driver, view_email_template_page, template_name)

@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_email_template_file_management_settings(driver, login_seeded_user):
    # Test Creating an email template and attach a file to it
    template_name = f"Functional Tests - test email file management settings- {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    assert view_email_template_page.get_file_added_count_text() == "1 file added"

    # Go to file management page
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"
    manage_files_page.click_manage_link(file_name)
    manage_a_file_page = ManageEmailTemplateFilePage(driver)
    assert manage_a_file_page.get_h1_text() == file_name

    # Change link text
    link_text_label = "Link text"
    original_link_text = manage_a_file_page.get_file_setting_value(link_text_label)
    assert original_link_text == "Not set"
    manage_a_file_page.click_change_file_setting(link_text_label)
    change_link_text_page = ChangeLinkTextForEmailFilePage(driver)
    assert change_link_text_page.get_h1_text() == "Add link text"
    new_link_text = "file_download_link"
    change_link_text_page.fill_in_link_text(new_link_text)
    change_link_text_page.click_continue_button()

    # confirm link text change
    assert manage_a_file_page.get_file_setting_value(link_text_label) == new_link_text

    # Change retention period
    retention_period_label = "Available for"
    original_retention_period_text = manage_a_file_page.get_file_setting_value(retention_period_label)
    assert original_retention_period_text == "26 weeks after sending\n        (about 6 months)"
    manage_a_file_page.click_change_file_setting(retention_period_label)
    assert change_link_text_page.get_h1_text() == "How long the file is available"
    change_retention_period = ChangeRentionPeriodForEmailFilePage(driver)
    new_retention_period = "50"
    change_retention_period.fill_in_retention_period(new_retention_period)
    change_retention_period.click_continue_button()

    # confirm retention period change
    assert (
        manage_a_file_page.get_file_setting_value(retention_period_label)
        == f"{new_retention_period} weeks after sending\n        (about 11 months)"
    )
    assert manage_a_file_page.get_h1_text() == file_name

    # Change email confirmation
    email_confirmation_label = "Ask recipient for email address"
    confirmation_label_choice = manage_a_file_page.get_file_setting_value(email_confirmation_label)
    assert confirmation_label_choice == "Yes"
    manage_a_file_page.click_change_file_setting(email_confirmation_label)
    email_confirmation_page = EmailConfirmationSettingForEmailFilePage(driver)
    assert email_confirmation_page.get_h1_text() == "Ask recipient for their email address"
    new_confirmation_label_choice = "No"
    email_confirmation_page.select_email_confirmation_option(new_confirmation_label_choice)
    email_confirmation_page.click_continue_button()

    # confirm email confirmation option change
    assert manage_a_file_page.get_h1_text() == file_name
    assert manage_a_file_page.get_file_setting_value(email_confirmation_label) == new_confirmation_label_choice

    # delete template which would also delete file
    manage_a_file_page.click_back_link()
    manage_files_page.click_back_link()
    assert view_email_template_page.get_h1_text() == template_name
    delete_email_template_for_send_file_via_ui_tests(driver, view_email_template_page, template_name)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_send_file_via_ui_preview_pages(driver, login_seeded_user, download_directory):
    # Test Creating an email template and attach a file to it
    template_name = f"Functional Tests - test email template file preview pages - {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # go to the individual file management page and change the link text
    view_email_template_page = ViewEmailTemplatePage(driver)
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    link_text_label = "Link text"
    new_link_text = "file_download_link"
    manage_files_page.click_manage_link(file_name)
    manage_a_file_page = ManageEmailTemplateFilePage(driver)
    manage_a_file_page.click_change_file_setting(link_text_label)
    change_link_text_page = ChangeLinkTextForEmailFilePage(driver)
    change_link_text_page.fill_in_link_text(new_link_text)
    change_link_text_page.click_continue_button()

    # go to template page and click on file link
    manage_a_file_page.click_back_link()
    manage_files_page.click_back_link()
    assert view_email_template_page.get_h1_text() == template_name
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
    # Create an email template
    template_name = f"Functional Tests - send email with file via csv - {uuid.uuid4()}"
    content = "Testing sending a one off email notification. with an email file. Test file below:"
    file_name = "attachment.pdf"
    template_id = create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    assert view_email_template_page.get_file_added_count_text() == "1 file added"

    # go to the individual file management page and change the link text
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"
    link_text_label = "Link text"
    link_text = "file_download_link"
    manage_files_page.click_manage_link(file_name)
    manage_file_page = ManageEmailTemplateFilePage(driver)
    assert manage_file_page.get_h1_text() == file_name
    manage_file_page.click_change_file_setting(link_text_label)
    change_link_text_page = ChangeLinkTextForEmailFilePage(driver)
    assert change_link_text_page.get_h1_text() == "Add link text"
    change_link_text_page.fill_in_link_text(link_text)
    change_link_text_page.click_continue_button()

    manage_file_page.click_back_link()
    assert manage_file_page.get_h1_text() == "Manage files"
    manage_file_page.click_back_link()

    # send the email
    assert view_email_template_page.get_h1_text() == template_name
    assert link_text in view_email_template_page.get_email_message_body_content()
    view_email_template_page.click_send()

    set_sender_page = SendSetSenderPage(driver)
    set_sender_page.wait_until_current()
    assert set_sender_page.get_h1_text() == "Where should replies come back to?"
    set_sender_page.click_continue_button()

    send_via_csv_page = SendViaCsvPage(driver)
    # create temp csv for this test
    seeded_user_email = generate_unique_email(
        config["service"]["seeded_user"]["email"], "test_send_file_via_ui_preview_pages"
    )
    _, directory, csv_filename = create_temp_csv({"email address": seeded_user_email}, include_build_id=True)
    send_via_csv_page.go_to_upload_csv_for_service_and_template(config["service"]["id"], template_id)
    send_via_csv_page.upload_csv(directory, csv_filename)
    send_via_csv_preview_page = SendViaCsvPreviewPage(send_via_csv_page.driver)
    assert send_via_csv_preview_page.get_h1_text() == f"Preview of {template_name}"
    send_via_csv_preview_page.click_send()
    job_page = JobPage(driver)
    assert job_page.get_h1_text() == f"{csv_filename}"
    job_page.go_to_notification_page()

    # confirm that the email is being delivered
    send_email_confirmation_page = SentEmailMessagePage(driver)
    assert send_email_confirmation_page.get_h1_text() == "Email"
    status = send_email_confirmation_page.get_notification_status()
    assert "Delivering" in status or "Delivered"  # Either status pops up, depending on the test run

    # Confirm that the file download link sent to the recipient works
    # There are smoke tests and other tests covering the process of a recipient downloading
    # a document, so the whole journey will not be covered here
    send_email_confirmation_page.click_file_download_link(link_text)
    you_have_a_file_to_download_page = DocumentDownloadLandingPage(driver)
    assert you_have_a_file_to_download_page.get_h1_text() == "You have a file to download"
    you_have_a_file_to_download_page.go_to_download_page()

    # Go to service templates page and select the template
    base_url = config["notify_admin_url"]
    service_template_page_url = f"{base_url}/services/{config['service']['id']}/templates"
    you_have_a_file_to_download_page.get(service_template_page_url)
    templates_pages = ShowTemplatesPage(driver)
    assert templates_pages.get_h1_text() == "Templates"
    templates_pages.click_template_by_link_text(template_name)

    # delete the template
    assert view_email_template_page.get_h1_text() == template_name
    delete_email_template_for_send_file_via_ui_tests(driver, view_email_template_page, template_name)


def delete_email_template_for_send_file_via_ui_tests(driver, view_email_template_page, template_name):
    view_email_template_page.click_delete_template_link()
    view_email_template_page.click_template_deletion_confirmation_button()

    # confirm template has been deleted
    templates_page = ShowTemplatesPage(driver)
    assert templates_page.get_h1_text() == "Templates"
    assert template_name not in templates_page.get_all_listed_templates()
