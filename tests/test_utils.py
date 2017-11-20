import functools
import os
import tempfile
import csv
import re
import logging
import uuid
import pytest

from datetime import datetime
from retry import retry
from notifications_python_client.notifications import NotificationsAPIClient
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from config import Config
from tests.pages import (
    AddServicePage,
    DashboardPage,
    EditEmailTemplatePage,
    EmailReplyTo,
    InviteUserPage,
    MainPage,
    RegisterFromInvite,
    RegistrationPage,
    SelectTemplatePage,
    ShowTemplatesPage,
    TeamMembersPage,
    VerifyPage
)

logging.basicConfig(filename='./logs/test_run_{}.log'.format(datetime.utcnow()),
                    level=logging.INFO)

jenkins_build_id = os.getenv('BUILD_ID', 'No build id')

email_address = "notify@digitial.cabinet-office.gov.uk"
email_address2 = "notify+1@digitial.cabinet-office.gov.uk"
email_address3 = "notify+2@digitial.cabinet-office.gov.uk"
default = " (default)"


def create_temp_csv(number, fieldnames):
    directory_name = tempfile.mkdtemp()
    csv_file_path = os.path.join(directory_name, 'sample.csv')
    with open(csv_file_path, 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerow({
            fieldnames[0]: number,
            fieldnames[1]: jenkins_build_id
        })
    return directory_name, 'sample.csv'


class RetryException(Exception):
    pass


def assert_notification_body(notification_id, notification):
    assert notification['id'] == notification_id
    assert 'The quick brown fox jumped over the lazy dog' in notification['body']


def generate_unique_email(email, uuid):
    parts = email.split('@')
    return "{}+{}@{}".format(parts[0], uuid, parts[1])


def get_link(profile, template_id, email):
    email_body = get_notification_via_api(
        template_id,
        profile.notify_service_api_key,
        email
    )
    match = re.search(r'http[s]?://\S+', email_body, re.MULTILINE)
    if match:
        return match.group(0)
    else:
        pytest.fail("Couldn't get the registraion link from the email")


@retry(RetryException, tries=Config.VERIFY_CODE_RETRY_TIMES, delay=Config.VERIFY_CODE_RETRY_INTERVAL)
def do_verify(driver, profile):
    try:
        verify_code = get_verify_code_from_api(profile)
        verify_page = VerifyPage(driver)
        verify_page.verify(verify_code)
        driver.find_element_by_class_name('error-message')
    except (NoSuchElementException, TimeoutException) as e:
        #  In some cases a TimeoutException is raised even if we have managed to verify.
        #  For now, check explicitly if we 'have verified' and if so move on.
        return True
    else:
        #  There was an error message so let's retry
        raise RetryException


def do_user_registration(driver, profile, base_url):
    main_page = MainPage(driver)
    main_page.get()
    main_page.click_set_up_account()

    registration_page = RegistrationPage(driver)
    assert registration_page.is_current()

    registration_page.register(profile)

    assert driver.current_url == base_url + '/registration-continue'

    registration_link = get_link(profile,
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


def do_user_can_invite_someone_to_notify(driver, profile, base_url):

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
    invite_user_page.sign_out()
    invite_user_page.wait_until_url_is(base_url)

    # next part of interaction is from point of view of invitee
    # i.e. after visting invite_link we'll be registering using invite_email
    # but use same mobile number and password as profile

    invite_link = get_link(profile, profile.invitation_template_id, invite_email)
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
    dashboard_page.wait_until_url_is(base_url)


def do_edit_and_delete_email_template(driver):
    test_name = 'edit/delete test'
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()
    dashboard_page.click_templates()

    existing_templates = [x.text for x in driver.find_elements_by_class_name('message-name')]

    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_add_new_template()

    select_template_page = SelectTemplatePage(driver)
    select_template_page.select_email()
    select_template_page.click_continue()

    template_page = EditEmailTemplatePage(driver)
    template_page.create_template(name=test_name)
    template_page.click_templates()

    assert test_name in [x.text for x in driver.find_elements_by_class_name('message-name')]

    show_templates_page.click_template_by_link_text(test_name)
    template_page.click_delete()

    assert [x.text for x in driver.find_elements_by_class_name('message-name')] == existing_templates


def get_verify_code_from_api(profile):
    verify_code_message = get_notification_via_api(
        Config.VERIFY_CODE_TEMPLATE_ID,
        Config.NOTIFY_SERVICE_API_KEY,
        profile.mobile
    )
    m = re.search(r'\d{5}', verify_code_message)
    if not m:
        pytest.fail("Could not find the verify code in notification body")
    print('Trying to use 2fa code:', m.group(0))
    return m.group(0)


@retry(RetryException, tries=Config.NOTIFICATION_RETRY_TIMES, delay=Config.NOTIFICATION_RETRY_INTERVAL)
def get_notification_via_api(template_id, api_key, sent_to):
    client = NotificationsAPIClient(
        base_url=Config.NOTIFY_API_URL,
        api_key=api_key
    )
    resp = client.get('v2/notifications', params={'include_jobs': True})
    for notification in resp['notifications']:
        t_id = notification['template']['id']
        to = notification['email_address'] or notification['phone_number']
        status = notification['status']
        if t_id == template_id and to == sent_to and status in ['sending', 'delivered']:
            return notification['body']
    message = 'Could not find notification with template {} to {} with a status of sending or delivered' \
        .format(template_id,
                sent_to)
    raise RetryException(message)


def recordtime(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.info('Starting Test: {}'.format(func.__name__))
            logging.info('Start Time: {}'.format(str(datetime.utcnow())))
            result = func(*args, **kwargs)
            return result
        finally:
            logging.info('End Time: {}'.format(str(datetime.utcnow())))

    return wrapper


def do_user_can_add_reply_to_email_to_service(driver):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()

    service_id = dashboard_page.get_service_id()

    email_reply_to_page = EmailReplyTo(driver)

    email_reply_to_page.go_to_add_email_reply_to_address(service_id)
    email_reply_to_page.insert_email_reply_to_address(email_address)
    email_reply_to_page.click_add_email_reply_to()

    body = email_reply_to_page.get_reply_to_email_addresses()

    assert email_address + default in body.text
    assert email_address2 not in body.text
    assert email_address3 not in body.text

    dashboard_page.go_to_dashboard_for_service(service_id)


def do_user_can_update_reply_to_email_to_service(driver):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()

    service_id = dashboard_page.get_service_id()

    email_reply_to_page = EmailReplyTo(driver)

    email_reply_to_page.go_to_add_email_reply_to_address(service_id)
    email_reply_to_page.insert_email_reply_to_address(email_address2)
    email_reply_to_page.click_add_email_reply_to()

    body = email_reply_to_page.get_reply_to_email_addresses()

    assert email_address + default in body.text
    assert email_address2 in body.text

    sub_body = body.text[body.text.index(email_address2):]  # find the index of the email address
    email_reply_to_id = sub_body.split('\n')[2]  # the id is the third entry [ 'email address, 'Change', id' ]

    email_reply_to_page.go_to_edit_email_reply_to_address(service_id, email_reply_to_id)
    email_reply_to_page.clear_email_reply_to()
    email_reply_to_page.insert_email_reply_to_address(email_address3)
    email_reply_to_page.check_is_default_check_box()
    email_reply_to_page.click_add_email_reply_to()

    body = email_reply_to_page.get_reply_to_email_addresses()

    assert email_address in body.text
    assert email_address2 not in body.text
    assert email_address3 + default in body.text

    dashboard_page.go_to_dashboard_for_service(service_id)
