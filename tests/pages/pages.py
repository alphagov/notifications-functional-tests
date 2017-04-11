import os
import shutil

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from retry import retry
from config import Config

from tests.pages.element import (
    EmailInputElement,
    PasswordInputElement,
    SmsInputElement,
    NameInputElement,
    MobileInputElement,
    ServiceInputElement,
    TemplateContentElement,
    FileInputElement,
    SubjectInputElement,
    KeyNameInputElement
)


from tests.pages.locators import (
    CommonPageLocators,
    MainPageLocators,
    AddServicePageLocators,
    DashboardPageLocators,
    NavigationLocators,
    TemplatePageLocators,
    EditTemplatePageLocators,
    UploadCsvLocators,
    TeamMembersPageLocators,
    InviteUserPageLocators,
    ApiKeysPageLocators,
    VerifyPageLocators
)


class RetryException(Exception):
    pass


class BasePage(object):

    base_url = Config.NOTIFY_ADMIN_URL
    sign_out_link = NavigationLocators.SIGN_OUT_LINK

    def __init__(self, driver):
        self.driver = driver

    def wait_for_invisible_element(self, locator):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(locator)
        )

    def wait_for_element(self, locator):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(locator),
            EC.presence_of_element_located(locator)
        )

    def sign_out(self):
        element = self.wait_for_element(BasePage.sign_out_link)
        element.click()
        self.driver.delete_all_cookies()

    def wait_until_url_is(self, url):
        return WebDriverWait(self.driver, 10).until(
            self.url_contains(url)
        )

    def url_contains(self, url):
        def check_contains_url(driver):
            return url in self.driver.current_url
        return check_contains_url

    def select_checkbox_or_radio(self, element):
        self.driver.execute_script("arguments[0].setAttribute('checked', 'checked')", element)


class MainPage(BasePage):

    set_up_account_button = MainPageLocators.SETUP_ACCOUNT_BUTTON

    def get(self):
        self.driver.get(self.base_url)

    def click_set_up_account(self):
        element = self.wait_for_element(MainPage.set_up_account_button)
        element.click()


class RegistrationPage(BasePage):

    name_input = NameInputElement()
    email_input = EmailInputElement()
    mobile_input = MobileInputElement()
    password_input = PasswordInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def is_current(self):
        return self.wait_until_url_is(self.base_url + '/register')

    def register(self, profile):
        self.name_input = profile.name
        self.email_input = profile.email
        self.mobile_input = profile.mobile
        self.password_input = profile.password
        self.click_continue_button()

    def click_continue_button(self):
        element = self.wait_for_element(RegistrationPage.continue_button)
        element.click()


class AddServicePage(BasePage):

    service_input = ServiceInputElement()
    add_service_button = AddServicePageLocators.ADD_SERVICE_BUTTON

    def is_current(self):
        return self.wait_until_url_is(self.base_url + '/add-service?first=first')

    def add_service(self, name):
        self.service_input = name
        self.click_add_service_button()

    def click_add_service_button(self):
        element = self.wait_for_element(AddServicePage.add_service_button)
        element.click()


class SignInPage(BasePage):

    email_input = EmailInputElement()
    password_input = PasswordInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def get(self):
        self.driver.get(self.base_url + '/sign-in')

    def is_current(self):
        return self.wait_until_url_is(self.base_url + '/sign-in')

    def fill_login_form(self, profile, seeded=False):
        if not seeded:
            self.email_input = profile.email
            self.password_input = profile.password
        else:
            self.email_input = profile.notify_research_service_email
            self.password_input = profile.notify_research_service_password

    def click_continue_button(self):
        element = self.wait_for_element(SignInPage.continue_button)
        element.click()

    def login(self, profile, seeded=False):
        self.fill_login_form(profile, seeded)
        self.click_continue_button()


class VerifyPage(BasePage):

    sms_input = SmsInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def click_continue_button(self):
        element = self.wait_for_element(VerifyPage.continue_button)
        element.click()

    def verify(self, code):
        element = self.wait_for_element(VerifyPageLocators.SMS_INPUT)
        element.clear()
        self.sms_input = code
        self.click_continue_button()

    def has_code_error(self):
        try:
            self.driver.find_element_by_class_name('error-message')
        except NoSuchElementException:
            return False
        return True


class DashboardPage(BasePage):

    h2 = DashboardPageLocators.H2
    sms_templates_link = DashboardPageLocators.SMS_TEMPLATES_LINK
    email_templates_link = DashboardPageLocators.EMAIL_TEMPLATES_LINK
    team_members_link = DashboardPageLocators.TEAM_MEMBERS_LINK
    api_keys_link = DashboardPageLocators.API_KEYS_LINK
    total_email_div = DashboardPageLocators.TOTAL_EMAIL_NUMBER
    total_sms_div = DashboardPageLocators.TOTAL_SMS_NUMBER

    def _message_count_for_template_div(self, template_id):
        return DashboardPageLocators.messages_sent_count_for_template(template_id)

    def is_current(self, service_id):
        expected = '{}/services/{}/dashboard'.format(self.base_url, service_id)
        return self.driver.current_url == expected

    def h2_is_service_name(self, expected_name):
        element = self.wait_for_element(DashboardPage.h2)
        return expected_name == element.text

    def click_sms_templates(self):
        element = self.wait_for_element(DashboardPage.sms_templates_link)
        element.click()

    def click_email_templates(self):
        element = self.wait_for_element(DashboardPage.email_templates_link)
        element.click()

    def click_team_members_link(self):
        element = self.wait_for_element(DashboardPage.team_members_link)
        element.click()

    def click_user_profile_link(self, link_text):
        element = self.wait_for_element((By.LINK_TEXT, link_text))
        element.click()

    def click_api_keys_link(self):
        element = self.wait_for_element(DashboardPage.api_keys_link)
        element.click()

    def get_service_id(self):
        return self.driver.current_url.split('/services/')[1].split('/')[0]

    def go_to_dashboard_for_service(self, service_id=None):
        if not service_id:
            service_id = self.get_service_id()
        url = "{}/services/{}/dashboard".format(self.base_url, service_id)
        self.driver.get(url)

    def get_total_message_count(self, message_type):
        target_div = DashboardPage.total_email_div if message_type == 'email' else DashboardPage.total_sms_div
        element = self.wait_for_element(target_div)

        return int(element.text)

    def get_template_message_count(self, template_id):
        messages_sent_count_for_template_div = self._message_count_for_template_div(template_id)
        element = self.wait_for_element(messages_sent_count_for_template_div)

        return int(element.text)


class SendSmsTemplatePage(BasePage):

    new_sms_template_link = TemplatePageLocators.ADD_NEW_TEMPLATE_LINK
    edit_sms_template_link = TemplatePageLocators.EDIT_TEMPLATE_LINK

    def click_add_new_template(self):
        element = self.wait_for_element(SendSmsTemplatePage.new_sms_template_link)
        element.click()

    def click_edit_template(self):
        element = self.wait_for_element(SendSmsTemplatePage.edit_sms_template_link)
        element.click()

    def click_upload_recipients(self):
        element = self.wait_for_element(TemplatePageLocators.UPLOAD_RECIPIENTS_LINK)
        element.click()


class EditSmsTemplatePage(BasePage):

    name_input = NameInputElement()
    template_content_input = TemplateContentElement()
    save_button = EditTemplatePageLocators.SAVE_BUTTON

    def click_save(self):
        element = self.wait_for_element(EditSmsTemplatePage.save_button)
        element.click()

    def create_template(self, name='Test email template'):
        self.name_input = name
        self.template_content_input = 'The quick brown fox jumped over the lazy dog. Jenkins job id: ((build_id))'
        self.click_save()

    def get_id(self):
        # e.g.
        # http://localhost:6012/services/237dd966-b092-42ab-b406-0a00187d007f/templates/4808eb34-5225-492b-8af2-14b232f05b8e/edit
        # circle back and do better
        return self.driver.current_url.split('/templates/')[1].split('/')[0]


class SendEmailTemplatePage(BasePage):

    add_a_new_email_template_link = TemplatePageLocators.ADD_A_NEW_TEMPLATE_LINK
    add_new_email_template_link = TemplatePageLocators.ADD_NEW_TEMPLATE_LINK
    edit_email_template_link = TemplatePageLocators.EDIT_TEMPLATE_LINK

    def click_add_a_new_template(self):
        element = self.wait_for_element(SendEmailTemplatePage.add_a_new_email_template_link)
        element.click()

    def click_add_new_template(self):
        element = self.wait_for_element(SendEmailTemplatePage.add_new_email_template_link)
        element.click()

    def click_edit_template(self):
        element = self.wait_for_element(SendEmailTemplatePage.edit_email_template_link)
        element.click()

    def click_upload_recipients(self):
        element = self.wait_for_element(TemplatePageLocators.UPLOAD_RECIPIENTS_LINK)
        element.click()


class EditEmailTemplatePage(BasePage):

    name_input = NameInputElement()
    subject_input = SubjectInputElement()
    template_content_input = TemplateContentElement()
    save_button = EditTemplatePageLocators.SAVE_BUTTON
    delete_button = EditTemplatePageLocators.DELETE_BUTTON
    confirm_delete_button = EditTemplatePageLocators.CONFIRM_DELETE_BUTTON

    def click_save(self):
        element = self.wait_for_element(EditEmailTemplatePage.save_button)
        element.click()

    def click_delete(self):
        element = self.wait_for_element(EditEmailTemplatePage.delete_button)
        element.click()
        element = self.wait_for_element(EditEmailTemplatePage.confirm_delete_button)
        element.click()

    def create_template(self, name='Test email template'):
        self.name_input = name
        self.subject_input = 'Test email from functional tests'
        self.template_content_input = 'The quick brown fox jumped over the lazy dog. Jenkins job id: ((build_id))'
        self.click_save()

    def get_id(self):
        # e.g.
        # http://localhost:6012/services/237dd966-b092-42ab-b406-0a00187d007f/templates/4808eb34-5225-492b-8af2-14b232f05b8e/edit
        # circle back and do better
        return self.driver.current_url.split('/templates/')[1].split('/')[0]


class UploadCsvPage(BasePage):

    file_input_element = FileInputElement()
    send_button = UploadCsvLocators.SEND_BUTTON
    first_notification = UploadCsvLocators.FIRST_NOTIFICATION_AFTER_UPLOAD

    def click_send(self):
        element = self.wait_for_element(UploadCsvPage.send_button)
        element.click()

    def upload_csv(self, directory, path):
        file_path = os.path.join(directory, 'sample.csv')
        self.file_input_element = file_path
        self.click_send()
        shutil.rmtree(directory, ignore_errors=True)

    @retry(RetryException, tries=5, delay=10)
    def get_notification_id_after_upload(self):
        try:
            element = self.wait_for_element(UploadCsvPage.first_notification)
            notification_id = element.get_attribute('id')
            if not notification_id:
                raise RetryException('No notification id yet {}'.format(notification_id))
            else:
                return notification_id
        except StaleElementReferenceException:
            raise RetryException('Could not find element...')

    def go_to_upload_csv_for_service_and_template(self, service_id, template_id):
        url = "{}/services/{}/send/{}/csv".format(self.base_url, service_id, template_id)
        self.driver.get(url)

    def get_template_id(self):
        return self.driver.current_url.split('//')[1].split('/')[4].split('?')[0]


class TeamMembersPage(BasePage):

    h1 = TeamMembersPageLocators.H1
    invite_team_member_button = TeamMembersPageLocators.INVITE_TEAM_MEMBER_BUTTON

    def h1_is_team_members(self):
        element = self.wait_for_element(TeamMembersPage.h1)
        return element.text == 'Team members'

    def click_invite_user(self):
        element = self.wait_for_element(TeamMembersPage.invite_team_member_button)
        element.click()


class InviteUserPage(BasePage):

    email_input = EmailInputElement()
    send_messages_checkbox = InviteUserPageLocators.SEND_MESSAGES_CHECKBOX
    manage_services_checkbox = InviteUserPageLocators.MANAGE_SERVICES_CHECKBOX
    manage_api_keys_checkbox = InviteUserPageLocators.MANAGE_API_KEYS_CHECKBOX
    send_invitation_button = InviteUserPageLocators.SEND_INVITATION_BUTTON

    def fill_invitation_form(self, email, send_messages=False, manage_services=False, manage_api_keys=False):
        self.email_input = email
        if send_messages:
            element = self.wait_for_invisible_element(InviteUserPage.send_messages_checkbox)
            self.select_checkbox_or_radio(element)
        if manage_services:
            element = self.wait_for_invisible_element(InviteUserPage.manage_services_checkbox)
            self.select_checkbox_or_radio(element)
        if manage_api_keys:
            element = self.wait_for_invisible_element(InviteUserPage.manage_api_keys_checkbox)
            self.select_checkbox_or_radio(element)

    def send_invitation(self):
        element = self.wait_for_element(InviteUserPage.send_invitation_button)
        element.click()


class RegisterFromInvite(BasePage):

    name_input = NameInputElement()
    mobile_input = MobileInputElement()
    password_input = PasswordInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def fill_registration_form(self, name, profile):
        self.name_input = name
        self.mobile_input = profile.mobile
        self.password_input = profile.password

    def click_continue(self):
        element = self.wait_for_element(RegisterFromInvite.continue_button)
        element.click()


class ProfilePage(BasePage):

    h1 = CommonPageLocators.H1

    def h1_is_correct(self):
        element = self.wait_for_element(ProfilePage.h1)
        return element.text == 'Your profile'


class ApiKeyPage(BasePage):

    key_name_input = KeyNameInputElement()
    keys_link = ApiKeysPageLocators.KEYS_PAGE_LINK
    create_key_link = ApiKeysPageLocators.CREATE_KEY_LINK
    continue_button = CommonPageLocators.CONTINUE_BUTTON
    api_key_element = ApiKeysPageLocators.API_KEY_ELEMENT
    key_types = {
        'normal': ApiKeysPageLocators.NORMAL_KEY_RADIO,
        'test': ApiKeysPageLocators.TEST_KEY_RADIO,
        'team': ApiKeysPageLocators.TEAM_KEY_RADIO,
    }

    def enter_key_name(self, key_type='normal'):
        self.key_name_input = 'Test ' + key_type

    def click_keys_link(self):
        element = self.wait_for_element(ApiKeyPage.keys_link)
        element.click()

    def click_create_key(self):
        element = self.wait_for_element(ApiKeyPage.create_key_link)
        element.click()

    def click_continue(self):
        element = self.wait_for_element(ApiKeyPage.continue_button)
        element.click()

    def get_api_key(self):
        element = self.wait_for_element(ApiKeyPage.api_key_element)
        return element.text

    def click_key_type_radio(self, key_type='normal'):
        element = self.wait_for_invisible_element(ApiKeyPage.key_types[key_type])
        self.select_checkbox_or_radio(element)
