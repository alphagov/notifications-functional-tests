import csv
import functools
import logging
import os
import re
import tempfile
import time
import uuid
from datetime import UTC, datetime

from filelock import FileLock
from notifications_python_client.notifications import NotificationsAPIClient
from retry import retry
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from config import config, generate_unique_email
from tests.pages import (
    AddServicePage,
    ConfirmEditLetterTemplatePage,
    DashboardPage,
    EditEmailTemplatePage,
    EditLetterTemplatePage,
    EditSmsTemplatePage,
    EmailReplyTo,
    InviteUserPage,
    MainPage,
    ManageAttachmentPage,
    RegisterFromInvite,
    RegistrationPage,
    SendLetterPreviewPage,
    SendOneRecipient,
    ShowTemplatesPage,
    SmsSenderPage,
    TeamMembersPage,
    UploadAttachmentPage,
    VerifyPage,
    ViewLetterTemplatePage,
    ViewTemplatePage,
    YourServicesPage,
)
from tests.pages.pages import RenameLetterTemplatePage

logging.basicConfig(filename=f"./logs/test_run_{datetime.now(UTC)}.log", level=logging.INFO)

default = " (default)"


class NotificationStatuses:
    VIRUS_SCAN_FAILED = "virus-scan-failed"
    ACCEPTED = {"accepted"}
    RECEIVED = {"received"}
    DELIVERED = {"delivered", "temporary-failure", "permanent-failure"}
    SENT = RECEIVED | DELIVERED | {"sending", "pending"}


def create_temp_csv(fields):
    directory_name = tempfile.mkdtemp()
    csv_filename = f"{uuid.uuid4()}-sample.csv"
    csv_file_path = os.path.join(directory_name, csv_filename)
    fields.update({"build_id": "No build id"})
    with open(csv_file_path, "w") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fields.keys())
        csv_writer.writeheader()
        csv_writer.writerow(fields)
    return directory_name, csv_filename


def convert_naive_utc_datetime_to_cap_standard_string(dt):
    """
    As defined in section 3.3.2 of
    http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html
    They define the standard "YYYY-MM-DDThh:mm:ssXzh:zm", where X is
    `+` if the timezone is > UTC, otherwise `-`
    """
    return f"{dt.strftime('%Y-%m-%dT%H:%M:%S')}-00:00"


class RetryException(Exception):
    pass


def assert_notification_body(notification_id, notification):
    assert notification["id"] == notification_id
    assert "The quick brown fox jumped over the lazy dog" in notification["body"]


def get_link(template_id, email):
    email_body = get_notification_by_to_field(template_id, config["notify_service_api_key"], email)
    m = re.search(r"http[s]?://\S+", email_body, re.MULTILINE)
    if not m:
        raise RetryException(f"Could not find a verify email code for template {template_id} sent to {email}")
    return m.group(0)


@retry(
    RetryException,
    tries=config["verify_code_retry_times"],
    delay=config["verify_code_retry_interval"],
)
def do_verify(driver, mobile_number):
    verify_page = VerifyPage(driver)

    # Retry verification up to 3 times
    for i in range(3):
        time.sleep(1) # wait a moment for the code to arrive
        verify_code = get_verify_code_from_api(mobile_number)
        verify_page.verify(verify_code)

        if verify_page.verify_code_successful():
            return

    # If all 3 attempts failed, raise an exception
    raise RetryException("Verification failed after 3 attempts")


def do_email_auth_verify(driver):
    do_email_verification(
        driver,
        config["notify_templates"]["email_auth_template_id"],
        config["service"]["email_auth_account"],
    )


@retry(
    RetryException,
    tries=config["verify_code_retry_times"],
    delay=config["verify_code_retry_interval"],
)
def do_email_verification(driver, template_id, email_address):
    try:
        email_link = get_link(template_id, email_address)
        driver.get(email_link)

        if driver.find_element(By.CLASS_NAME, "heading-large").text == "The link has expired":
            #  There was an error message (presumably we tried to use an email token that was already used/expired)
            raise RetryException

    except (NoSuchElementException, TimeoutException):
        # no error - that means we're logged in! hurray.
        return True


def do_user_add_new_service(driver):
    your_service_page = YourServicesPage(driver)
    # for functional tests to run, there needs to be a functional test organisation that:
    # * has the `ask to join a service` flag enabled
    # * has the functional tests email domain (by default digital.cabinet-office.gov.uk) set as a known domain
    your_service_page.wait_until_current()
    your_service_page.add_new_service()

    add_service_page = AddServicePage(driver)
    add_service_page.wait_until_current()
    add_service_page.add_service(config["service_name"])

    dashboard_page = DashboardPage(driver)
    service_id = dashboard_page.get_service_id()
    dashboard_page.go_to_dashboard_for_service(service_id)

    assert dashboard_page.get_service_name() == config["service_name"]


def do_user_registration(driver):
    main_page = MainPage(driver)
    main_page.get()
    main_page.click_set_up_account()

    registration_page = RegistrationPage(driver)
    registration_page.wait_until_current()

    registration_page.register()

    registration_page.wait_until_url_contains("/registration-continue")

    registration_link = get_link(config["notify_templates"]["registration_template_id"], config["user"]["email"])

    driver.get(registration_link)

    do_verify(driver, config["user"]["mobile"])


def do_user_can_invite_someone_to_notify(driver, basic_view):
    dashboard_page = DashboardPage(driver)
    dashboard_page.click_team_members_link()

    team_members_page = TeamMembersPage(driver)
    assert team_members_page.h1_is_team_members()
    team_members_page.click_invite_user()

    invite_user_page = InviteUserPage(driver)

    invited_user_randomness = str(uuid.uuid1())
    invited_user_name = "Invited User " + invited_user_randomness
    invite_email = generate_unique_email(config["user"]["email"], invited_user_randomness)
    if basic_view:
        invite_user_page.fill_invitation_form(invite_email, send_messages_only=True)
    else:
        invite_user_page.fill_invitation_form(invite_email, send_messages_only=False)

    invite_user_page.send_invitation()
    invite_user_page.sign_out()
    invite_user_page.wait_until_url_contains(config["notify_admin_url"])

    # next part of interaction is from point of view of invitee
    # i.e. after visting invite_link we'll be registering using invite_email
    # but use same mobile number and password as profile

    invite_link = get_link(config["notify_templates"]["invitation_template_id"], invite_email)
    driver.get(invite_link)
    register_from_invite_page = RegisterFromInvite(driver)
    register_from_invite_page.fill_registration_form(invited_user_name)
    register_from_invite_page.click_continue()

    do_verify(driver, config["user"]["mobile"])
    dashboard_page = DashboardPage(driver)
    service_id = dashboard_page.get_service_id()
    dashboard_page.go_to_dashboard_for_service(service_id)

    assert dashboard_page.get_service_name() == config["service_name"]
    if basic_view:
        is_basic_view(dashboard_page)
    else:
        is_view_for_all_permissions(dashboard_page)


def is_basic_view(dashboard_page):
    assert dashboard_page.get_navigation_list() == "Templates\nSent messages\nUploads\nTeam members"
    assert dashboard_page.wait_until_url_contains(f"/services/{dashboard_page.get_service_id()}/templates")


def is_view_for_all_permissions(page):
    assert page.get_navigation_list() == (
        "Dashboard\nTemplates\nUploads\nTeam members\nUsage\nSettings\nAPI integration\nMake your service live"
    )
    expected = f"/services/{page.get_service_id()}"
    assert page.wait_until_url_contains(expected)


def create_email_template(driver, name, content=None, has_unsubscribe_link=False):
    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_add_new_template()

    show_templates_page.select_email()

    template_page = EditEmailTemplatePage(driver)
    template_page.fill_template(name=name, content=content, has_unsubscribe_link=has_unsubscribe_link)
    return template_page.get_template_id()


def create_sms_template(driver, name, content=None):
    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_add_new_template()

    show_templates_page.select_text_message()

    template_page = EditSmsTemplatePage(driver)
    template_page.fill_template(name=name, content=content)
    return template_page.get_template_id()


def create_letter_template(driver, name, content=None):
    show_templates_page = ShowTemplatesPage(driver)

    # Letter templates are created with a generic name 'Untitled letter template' - so if two tests create a
    # template at the same time they might get their wires crossed.
    lockfile = os.path.join(tempfile.gettempdir(), "create-letter-template.lock")
    with FileLock(lockfile):
        show_templates_page.click_add_new_template()

        show_templates_page.select_letter()

        view_template_page = ViewLetterTemplatePage(driver)
        view_template_page.click_edit_body()

        edit_template_page = EditLetterTemplatePage(driver)
        edit_template_page.create_template(content=content)

        confirm_edit_template_page = ConfirmEditLetterTemplatePage(driver)
        confirm_edit_template_page.click_save()

        view_template_page = ViewLetterTemplatePage(driver)
        view_template_page.click_rename_link()

        rename_template_page = RenameLetterTemplatePage(driver)
        rename_template_page.rename_template(name)

    return confirm_edit_template_page.get_template_id()


def go_to_templates_page(driver, service="service"):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config[service]["id"])
    dashboard_page.click_templates()


def edit_sms_template(driver, template_name, new_template_name, content, service="service"):
    show_templates_page = ShowTemplatesPage(driver)
    try:
        show_templates_page.click_template_by_link_text(template_name)
    except TimeoutException:
        dashboard_page = DashboardPage(driver)
        dashboard_page.go_to_dashboard_for_service(config[service]["id"])
        dashboard_page.click_templates()
        show_templates_page.click_template_by_link_text(template_name)

    template_page = ViewTemplatePage(driver)
    template_page.click_edit()

    edit_sms_template_page = EditSmsTemplatePage(driver)
    edit_sms_template_page.fill_template(name=new_template_name, content=content)


def edit_email_template(driver, template_name, new_template_name, subject, content, service="service"):
    show_templates_page = ShowTemplatesPage(driver)
    try:
        show_templates_page.click_template_by_link_text(template_name)
    except TimeoutException:
        dashboard_page = DashboardPage(driver)
        dashboard_page.go_to_dashboard_for_service(config[service]["id"])
        dashboard_page.click_templates()
        show_templates_page.click_template_by_link_text(template_name)

    template_page = ViewTemplatePage(driver)
    template_page.click_edit()

    edit_email_template_page = EditEmailTemplatePage(driver)
    edit_email_template_page.fill_template(name=new_template_name, subject=subject, content=content)


def delete_template(driver, template_name, service="service"):
    show_templates_page = ShowTemplatesPage(driver)
    try:
        show_templates_page.click_template_by_link_text(template_name)
    except TimeoutException:
        dashboard_page = DashboardPage(driver)
        dashboard_page.go_to_dashboard_for_service(config[service]["id"])
        dashboard_page.click_templates()
        show_templates_page.click_template_by_link_text(template_name)
    template_page = EditEmailTemplatePage(driver)
    template_page.click_delete()


def add_letter_attachment_for_template(driver, name, service="service"):
    show_templates_page = ShowTemplatesPage(driver)
    try:
        show_templates_page.click_template_by_link_text(name)
    except TimeoutException:
        dashboard_page = DashboardPage(driver)
        dashboard_page.go_to_dashboard_for_service(config[service]["id"])
        dashboard_page.click_templates()
        show_templates_page.click_template_by_link_text(name)
    template_page = ViewLetterTemplatePage(driver)
    template_page.click_attachment_button()
    upload_page = UploadAttachmentPage(driver)
    upload_page.upload_attachment(os.path.join(os.getcwd(), "tests/test_files/attachment.pdf"))


def manage_letter_attachment(driver):
    template_page = ViewLetterTemplatePage(driver)
    template_page.click_attachment_button()


def delete_letter_attachment(driver):
    template_page = ManageAttachmentPage(driver)
    template_page.delete_attachment()


def get_verify_code_from_api(mobile_number):
    verify_code_message = get_notification_by_to_field(
        config["notify_templates"]["verify_code_template_id"],
        config["notify_service_api_key"],
        mobile_number,
    )
    m = re.search(r"\d{5}", verify_code_message)
    if not m:
        raise RetryException(
            "Could not find a verify code for template {} sent to {}".format(
                config["notify_templates"]["verify_code_template_id"], mobile_number
            )
        )
    return m.group(0)


def send_notification_to_one_recipient(
    driver,
    template_name,
    message_type,
    test=False,
    recipient_data=None,
    placeholders_number=None,
    test_name=None,
):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config["service"]["id"])
    dashboard_page.click_templates()

    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_template_by_link_text(template_name)
    view_template_page = ViewTemplatePage(driver)
    view_template_page.click_send()

    send_to_one_recipient_page = SendOneRecipient(driver)
    if message_type == "sms":
        send_to_one_recipient_page.choose_alternative_sms_sender()
    else:
        send_to_one_recipient_page.choose_alternative_sender()
    send_to_one_recipient_page.click_continue()
    if test is True:
        send_to_one_recipient_page.send_to_myself(message_type)
    else:
        send_to_one_recipient_page.enter_placeholder_value(recipient_data)
        send_to_one_recipient_page.click_continue()
    placeholders = []
    index = 0
    while send_to_one_recipient_page.is_page_title("Personalise this message"):
        if not send_to_one_recipient_page.is_placeholder_a_recipient_field(message_type):
            placeholder_value = str(uuid.uuid4())
            send_to_one_recipient_page.enter_placeholder_value(placeholder_value)
            placeholder_name = send_to_one_recipient_page.get_placeholder_name()
            placeholders.append({placeholder_name: placeholder_value})
        send_to_one_recipient_page.click_continue()
        index += 1
        if index > 10:
            raise TimeoutException("Too many attempts, something is broken with placeholders")
    if placeholders_number:
        assert len(placeholders) == placeholders_number
    for placeholder in placeholders:
        assert send_to_one_recipient_page.is_text_present_on_page(list(placeholder.values())[0])
    if message_type == "email":
        _assert_one_off_email_filled_in_properly(driver, template_name, test, recipient_data, test_name=test_name)
    else:
        _assert_one_off_sms_filled_in_properly(driver, template_name, test, recipient_data)
    return placeholders


def send_letter_to_one_recipient(driver, template_name, address, build_id):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config["service"]["id"])
    dashboard_page.click_templates()

    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_template_by_link_text(template_name)
    view_template_page = ViewTemplatePage(driver)
    view_template_page.click_send()

    send_to_one_recipient_page = SendOneRecipient(driver)
    send_to_one_recipient_page.send_to_address(address)
    send_to_one_recipient_page.enter_placeholder_value(build_id)
    send_to_one_recipient_page.click_continue()

    send_letter_preview_page = SendLetterPreviewPage(driver)
    send_letter_preview_page.click_send()


def send_bilingual_letter_to_one_recipient(driver, template_name, address, placeholders: dict):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config["service"]["id"])
    dashboard_page.click_templates()

    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_template_by_link_text(template_name)
    view_template_page = ViewTemplatePage(driver)
    view_template_page.click_send()

    send_to_one_recipient_page = SendOneRecipient(driver)
    send_to_one_recipient_page.send_to_address(address)
    for _ in range(len(placeholders)):
        send_to_one_recipient_page.enter_placeholder_value(
            placeholders[send_to_one_recipient_page.get_placeholder_name()]
        )
        send_to_one_recipient_page.click_continue()

    send_letter_preview_page = SendLetterPreviewPage(driver)
    send_letter_preview_page.click_send()


def _assert_one_off_sms_filled_in_properly(driver, template_name, test, recipient_number):
    sms_sender_page = SmsSenderPage(driver)
    sms_sender = sms_sender_page.get_sms_sender()
    sms_recipient = sms_sender_page.get_sms_recipient()

    assert sms_sender.text == "From: {}".format(config["service"]["sms_sender_text"])
    assert sms_recipient.text == f"To: {recipient_number}"
    assert sms_sender_page.is_page_title("Preview of ‘" + template_name + "’")


def _assert_one_off_email_filled_in_properly(driver, template_name, test, recipient_email, test_name=None):
    from tests.pages.rollups import get_email_and_password

    send_to_one_recipient_page = SendOneRecipient(driver)
    preview_rows = send_to_one_recipient_page.get_preview_contents()
    assert "From" in str(preview_rows[0].text)
    assert config["service"]["name"] in str(preview_rows[0].text)
    assert "Reply to" in str(preview_rows[1].text)
    assert config["service"]["email_reply_to"] in str(preview_rows[1].text)
    assert "To" in str(preview_rows[2].text)
    if test is True:
        email_address, _ = get_email_and_password("seeded", test_name=test_name)
        assert email_address in str(preview_rows[2].text)
    else:
        assert recipient_email in str(preview_rows[2].text)
    assert "Subject" in str(preview_rows[3].text)
    assert send_to_one_recipient_page.is_page_title("Preview of ‘" + template_name + "’")


def get_notification_by_to_field(template_id, api_key, sent_to, statuses=None):
    client = NotificationsAPIClient(base_url=config["notify_api_url"], api_key=api_key)
    resp = client.get("v2/notifications")
    for notification in resp["notifications"]:
        t_id = notification["template"]["id"]
        to = notification["email_address"] or notification["phone_number"]
        if t_id == template_id and to == sent_to and (not statuses or notification["status"] in statuses):
            return notification["body"]
    return ""


def recordtime(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.info("Starting Test: %s", func.__name__)
            logging.info("Start Time: %s", str(datetime.now(UTC)))
            result = func(*args, **kwargs)
            return result
        finally:
            logging.info("End Time: %s", str(datetime.now(UTC)))

    return wrapper


def do_user_can_add_reply_to_email_to_service(driver):
    email_address = config["service"]["email_reply_to"]
    email_address2 = config["service"]["email_reply_to_2"]
    email_address3 = config["service"]["email_reply_to_3"]
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()

    service_id = dashboard_page.get_service_id()

    email_reply_to_page = EmailReplyTo(driver)

    email_reply_to_page.go_to_add_email_reply_to_address(service_id)
    email_reply_to_page.insert_email_reply_to_address(email_address)
    email_reply_to_page.click_add_email_reply_to()

    email_reply_to_page.click_continue_button(time=120)

    body = email_reply_to_page.get_reply_to_email_addresses()

    assert email_address + default in body.text
    assert email_address2 not in body.text
    assert email_address3 not in body.text

    dashboard_page.go_to_dashboard_for_service(service_id)


def do_user_can_update_reply_to_email_to_service(driver):
    email_address = config["service"]["email_reply_to"]
    email_address2 = config["service"]["email_reply_to_2"]
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()

    service_id = dashboard_page.get_service_id()

    email_reply_to_page = EmailReplyTo(driver)

    email_reply_to_page.go_to_add_email_reply_to_address(service_id)
    email_reply_to_page.insert_email_reply_to_address(email_address2)
    email_reply_to_page.click_add_email_reply_to()

    email_reply_to_page.click_continue_button(time=120)

    body = email_reply_to_page.get_reply_to_email_addresses()

    assert email_address + default in body.text
    assert email_address2 in body.text

    sub_body = body.text[body.text.index(email_address2) :]  # find the index of the email address
    # the id is the fifth entry [ 'email address, 'Change', 'email address', 'id label', id' ]
    email_reply_to_id = sub_body.split("\n")[4]

    email_reply_to_page.go_to_edit_email_reply_to_address(service_id, email_reply_to_id)
    email_reply_to_page.check_is_default_check_box()
    email_reply_to_page.click_add_email_reply_to()

    body = email_reply_to_page.get_reply_to_email_addresses()

    assert email_address in body.text
    assert email_address + default not in body.text
    assert email_address2 + default in body.text

    dashboard_page.go_to_dashboard_for_service(service_id)


@retry(
    RetryException,
    tries=10,
    delay=1,
)
def get_downloaded_document(download_directory, filename):
    """
    Wait up to ten seconds for the file to be downloaded, checking every second
    """
    for file in download_directory.iterdir():
        if file.is_file() and file.name == filename:
            return file
    raise RetryException(f"{filename} not found in downloads folder")


def pdf_page_has_text(pdf_page, expected_text, normalise_whitespace=True):
    page_text = pdf_page.extract_text()

    if normalise_whitespace:
        page_text = re.sub(r"\s+", " ", page_text.replace("\n", " "))

    return expected_text in page_text
