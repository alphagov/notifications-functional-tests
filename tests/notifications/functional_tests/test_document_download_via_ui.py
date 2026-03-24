import uuid

from config import config
from tests.pages import (
    ChangeLinkTextForEmailFilePage,
    ManageEmailTemplateFilePage,
    ManageFilesForEmailTemplatePage,
    ShowTemplatesPage,
    ViewEmailTemplatePage, SendSetSenderPage, SendOneRecipientPage, SendEmailPreviewPage, SendEmailConfirmationPage,
    YouHaveAFileToDownloadPage, ConfirmYourEmailAddressPage,
)
from tests.test_utils import (
    create_an_email_template_and_add_attach_a_file,
    delete_file_from_email_template_via_manage_files_page,
    recordtime,
)


@recordtime
def test_attaching_files_to_emails_and_also_deleting_them_via_ui(driver, login_seeded_user):
    # Create an email template
    template_name = f"Functional Tests - upload/delete file to email template - {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_add_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    assert view_email_template_page.get_file_added_count_text() == "1 file added"

    # Go to files list page
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"

    # Go to file management page for the file attached and delete file
    manage_files_page.click_manage_link(file_name)
    delete_file_from_email_template_via_manage_files_page(driver)

    # Confirm file has been removed on Preview email template page
    assert view_email_template_page.get_page_banner_text() == f"‘{file_name}’ has been removed"
    assert view_email_template_page.get_file_added_count_text() == "No files added"

    # delete template
    assert view_email_template_page.get_h1_text() == template_name
    view_email_template_page.click_delete_template_link()
    view_email_template_page.click_template_deletion_confirmation_button()

    # confirm template has been deleted
    templates_page = ShowTemplatesPage(driver)
    assert templates_page.get_h1_text() == "Templates"
    assert template_name not in templates_page.get_all_listed_templates()


@recordtime
def test_sending_a_file_one_off_via_document_download_via_ui(driver, login_seeded_user):
    # Create an email template
    template_name = f"Functional Tests - send a file off one off via ui - {uuid.uuid4()}"
    content = "Hi download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_add_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    assert view_email_template_page.get_file_added_count_text() == "1 file added"

    # go to the individual file management page and change the link text
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"
    link_text = "file_download_link"
    manage_files_page.click_manage_link(file_name)
    manage_file_page = ManageEmailTemplateFilePage(driver)
    assert manage_file_page.get_h1_text() == file_name
    manage_file_page.click_change_link_text()
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
    send_email_confirmation_page = SendEmailConfirmationPage(driver)
    assert send_email_confirmation_page.get_h1_text() == "Email"
    assert "Delivering" in send_email_confirmation_page.get_notification_status()

    # Confirm that the file download link sent to the recipient works
    # There are smoke tests and other tests covering the process of a recipient downloading
    # a document, so the whole journey will not be covered here
    send_email_confirmation_page.click_file_download_link(link_text)
    you_have_a_file_to_download_page = YouHaveAFileToDownloadPage(driver)
    assert you_have_a_file_to_download_page.get_h1_text() == "You have a file to download"
    you_have_a_file_to_download_page.click_continue_button()

    # Go to service templates page and select the template
    base_url = config["notify_admin_url"]
    service_template_page_url = f'{base_url}/services/{config["service"]["id"]}/templates'
    you_have_a_file_to_download_page.get(service_template_page_url)
    templates_pages = ShowTemplatesPage(driver)
    assert templates_pages.get_h1_text() == "Templates"
    templates_pages.click_template_by_link_text(template_name)

    # delete the template
    assert view_email_template_page.get_h1_text() == template_name
    view_email_template_page.click_delete_template_link()
    view_email_template_page.click_template_deletion_confirmation_button()

    # confirm template has been deleted
    templates_page = ShowTemplatesPage(driver)
    assert templates_page.get_h1_text() == "Templates"
    assert template_name not in templates_page.get_all_listed_templates()
