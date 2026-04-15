import uuid

import pytest
from pypdf import PdfReader

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
    SendEmailPreviewPage,
    SendOneRecipientPage,
    SendSetSenderPage,
    SendViaCsvPage,
    SentEmailMessagePage,
    ViewEmailTemplatePage,
)
from tests.postman import send_notification_via_csv
from tests.test_utils import (
    confirm_template_was_deleted,
    create_an_email_template_and_attach_a_file,
    delete_file_from_email_template_via_manage_files_page,
    delete_template,
    get_downloaded_document,
    go_to_templates_page,
    recordtime,
)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_attaching_files_to_emails_and_also_deleting_them_via_ui(driver, login_seeded_user):
    # Test Creating an email template and attach a file to it
    template_name = f"Functional Tests - upload/delete file to email template - {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    view_email_template_page = ViewEmailTemplatePage(driver)
    create_an_email_template_and_attach_a_file(
        driver=driver,
        file_name=file_name,
        template_name=template_name,
        content=content,
        view_email_template_page=view_email_template_page,
    )

    # Test removing the file from the template
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"
    manage_files_page.click_manage_link(file_name)
    delete_file_from_email_template_via_manage_files_page(driver)

    # Confirm file has been removed on Preview email template page
    assert view_email_template_page.get_page_banner_text() == f"‘{file_name}’ has been removed"
    assert view_email_template_page.get_file_added_count_text() == "No files added"

    # delete the template
    go_to_templates_page(driver)
    delete_template(driver, template_name)

    confirm_template_was_deleted(driver, template_name)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
@pytest.mark.parametrize("sending_mode", ["one_off", "via_csv"])
def test_send_email_with_file_via_ui(driver, login_seeded_user, sending_mode):
    # Create an email template
    template_name = f"Functional Tests - send one off email with file via ui - {uuid.uuid4()}"
    content = "Testing sending a one off email notification. with an email file. Test file below:"
    file_name = "attachment.pdf"
    view_email_template_page = ViewEmailTemplatePage(driver)
    create_an_email_template_and_attach_a_file(
        driver=driver,
        file_name=file_name,
        template_name=template_name,
        content=content,
        view_email_template_page=view_email_template_page,
    )

    link_text = "file_download_link"
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    manage_single_file_page = ManageEmailTemplateFilePage(driver)
    change_link_text_for_email_file(
        driver=driver,
        file_name=file_name,
        link_text=link_text,
        view_email_template_page=view_email_template_page,
        manage_files_page=manage_files_page,
        manage_single_file_page=manage_single_file_page,
    )

    manage_single_file_page.click_back_link()
    assert manage_single_file_page.get_h1_text() == "Manage files"
    manage_single_file_page.click_back_link()

    # send the email
    assert view_email_template_page.get_h1_text() == template_name
    assert link_text in view_email_template_page.get_email_message_body_content()

    template_id = view_email_template_page.get_template_id()
    view_email_template_page.click_send()

    set_sender_page = SendSetSenderPage(driver)
    set_sender_page.wait_until_current()
    assert set_sender_page.get_h1_text() == "Where should replies come back to?"
    set_sender_page.click_continue_button()
    if sending_mode == "one_off":
        send_to_one_recipient_page = SendOneRecipientPage(driver)
        assert send_to_one_recipient_page.get_h1_text() == f"Send ‘{template_name}’"
        send_to_one_recipient_page.send_to_myself("email")

        preview_send_one_recepient_page = SendEmailPreviewPage(driver)
        assert preview_send_one_recepient_page.get_h1_text() == f"Preview of ‘{template_name}’"
        preview_send_one_recepient_page.click_send_button()

    elif sending_mode == "via_csv":
        send_via_csv_page = SendViaCsvPage(driver)
        job_page = send_notification_via_csv(send_via_csv_page, "email", seeded=True, template_id=template_id)
        job_page.go_to_notification_page()

    # confirm that the email was sent
    sent_email_message_page = SentEmailMessagePage(driver)
    assert sent_email_message_page.get_h1_text() == "Email"

    # Confirm that the file download link sent to the recipient works
    # There are smoke tests and other tests covering the process of a recipient downloading
    # a document, so the whole journey will not be covered here
    sent_email_message_page.click_file_download_link(link_text)
    you_have_a_file_to_download_page = DocumentDownloadLandingPage(driver)
    assert you_have_a_file_to_download_page.get_h1_text() == "You have a file to download"
    you_have_a_file_to_download_page.go_to_download_page()

    # delete the template which will also archive the file attached
    go_to_templates_page(driver)
    delete_template(driver, template_name)

    confirm_template_was_deleted(driver, template_name)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_email_template_file_management_settings(driver, login_seeded_user):
    # Test Creating an email template and attach a file to it
    template_name = f"Functional Tests - test email file management settings- {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    view_email_template_page = ViewEmailTemplatePage(driver)
    create_an_email_template_and_attach_a_file(
        driver=driver,
        file_name=file_name,
        template_name=template_name,
        content=content,
        view_email_template_page=view_email_template_page,
    )

    link_text = "file_download_link"
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    manage_single_file_page = ManageEmailTemplateFilePage(driver)
    change_link_text_for_email_file(
        driver=driver,
        file_name=file_name,
        link_text=link_text,
        view_email_template_page=view_email_template_page,
        manage_files_page=manage_files_page,
        manage_single_file_page=manage_single_file_page,
    )

    # confirm link text change
    assert manage_single_file_page.get_file_setting_value("Link text") == link_text

    # Change retention period
    retention_period_label = "Available for"
    original_retention_period_text = manage_single_file_page.get_file_setting_value(retention_period_label)
    assert original_retention_period_text == "26 weeks after sending\n        (about 6 months)"
    manage_single_file_page.click_change_file_setting(retention_period_label)
    change_retention_period = ChangeRentionPeriodForEmailFilePage(driver)
    assert change_retention_period.get_h1_text() == "How long the file is available"
    new_retention_period = "50"
    change_retention_period.fill_in_retention_period(new_retention_period)
    change_retention_period.click_continue_button()

    # confirm retention period change
    assert (
        manage_single_file_page.get_file_setting_value(retention_period_label)
        == f"{new_retention_period} weeks after sending\n        (about 11 months)"
    )
    assert manage_single_file_page.get_h1_text() == file_name

    # Change email confirmation
    email_confirmation_label = "Ask recipient for email address"
    confirmation_label_choice = manage_single_file_page.get_file_setting_value(email_confirmation_label)
    assert confirmation_label_choice == "Yes"
    manage_single_file_page.click_change_file_setting(email_confirmation_label)
    email_confirmation_page = EmailConfirmationSettingForEmailFilePage(driver)
    assert email_confirmation_page.get_h1_text() == "Ask recipient for their email address"
    new_confirmation_label_choice = "No"
    email_confirmation_page.select_email_confirmation_option(new_confirmation_label_choice)
    email_confirmation_page.click_continue_button()

    # confirm email confirmation option change
    assert manage_single_file_page.get_h1_text() == file_name
    assert manage_single_file_page.get_file_setting_value(email_confirmation_label) == new_confirmation_label_choice

    # delete the template which will also archive the file attached
    go_to_templates_page(driver)
    delete_template(driver, template_name)

    confirm_template_was_deleted(driver, template_name)


@recordtime
@pytest.mark.xdist_group(name="send-files-via-ui-flow")
def test_send_file_via_ui_preview_pages(driver, login_seeded_user, download_directory):
    # Create an email template
    template_name = f"Functional Tests - send one off email with file via ui - {uuid.uuid4()}"
    content = "Testing sending a one off email notification. with an email file. Test file below:"
    file_name = "attachment.pdf"
    view_email_template_page = ViewEmailTemplatePage(driver)
    create_an_email_template_and_attach_a_file(
        driver=driver,
        file_name=file_name,
        template_name=template_name,
        content=content,
        view_email_template_page=view_email_template_page,
    )
    # Change link text for the email file
    link_text = "file_download_link"
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    manage_single_file_page = ManageEmailTemplateFilePage(driver)
    change_link_text_for_email_file(
        driver=driver,
        file_name=file_name,
        link_text=link_text,
        view_email_template_page=view_email_template_page,
        manage_files_page=manage_files_page,
        manage_single_file_page=manage_single_file_page,
    )

    # go to template page and click on file link
    manage_single_file_page.click_back_link()
    manage_files_page.click_back_link()
    assert view_email_template_page.get_h1_text() == template_name
    view_email_template_page.click_file_link_text(link_text)

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
    go_to_templates_page(driver)
    delete_template(driver, template_name)

    confirm_template_was_deleted(driver, template_name)


def change_link_text_for_email_file(
    driver, file_name, link_text, view_email_template_page, manage_files_page, manage_single_file_page
):
    view_email_template_page.click_manage_files_button()
    assert manage_files_page.get_h1_text() == "Manage files"
    manage_files_page.click_manage_link(file_name)
    assert manage_single_file_page.get_h1_text() == file_name
    manage_single_file_page.click_change_file_setting("Link text")
    change_link_text_page = ChangeLinkTextForEmailFilePage(driver)
    assert change_link_text_page.get_h1_text() == "Add link text"
    change_link_text_page.fill_in_link_text(link_text)
    change_link_text_page.click_continue_button()
