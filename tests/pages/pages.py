import os
import shutil

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    ApiKeysPageLocators
)


class BasePage(object):

    base_url = Config.NOTIFY_ADMIN_URL
    sign_out_link = NavigationLocators.SIGN_OUT_LINK

    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, locator):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(locator)
        )

    def sign_out(self):
        # getting and clicking on sign out link not working on travis
        self.driver.get(self.base_url+'/sign-out')


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
        return self.driver.current_url == self.base_url + '/register'

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
        return self.driver.current_url == self.base_url + '/add-service?first=first'

    def add_service(self, name):
        self.service_input = name
        self.click_add_service_button()

    def click_add_service_button(self):
        element = self.wait_for_element(AddServicePage.add_service_button)
        element.click()


class TourPage(BasePage):

    def is_current(self):
        return self.driver.current_url.endswith('/tour/1')

    def get_me_out_of_here(self):
        for i in range(0, 4):
            element = self.driver.find_element(By.LINK_TEXT, 'Next')
            element.click()


class SignInPage(BasePage):

    email_input = EmailInputElement()
    password_input = PasswordInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def get(self):
        self.driver.get(self.base_url+'/sign-in')

    def is_current(self):
        return self.driver.current_url == self.base_url+'/sign-in'

    def is_currect(self):
        return self.driver.current_url == self.base_url+'/sign-in'

    def fill_login_form(self, profile):
        self.email_input = profile.email
        self.password_input = profile.password

    def click_continue_button(self):
        element = self.wait_for_element(SignInPage.continue_button)
        element.click()

    def login(self, profile):
        self.fill_login_form(profile)
        self.click_continue_button()


class VerifyPage(BasePage):

    sms_input = SmsInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def is_current(self):
        return self.driver.current_url == self.base_url+'/verify'

    def click_continue_button(self):
        element = self.wait_for_element(VerifyPage.continue_button)
        element.click()

    def verify(self, code):
        self.sms_input = code
        self.click_continue_button()


class TwoFactorPage(BasePage):

    sms_input = SmsInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def is_current(self):
        return self.driver.current_url == self.base_url+'/two-factor'

    def click_continue_button(self):
        element = self.wait_for_element(TwoFactorPage.continue_button)
        element.click()

    def verify(self, code):
        self.sms_input = code
        self.click_continue_button()


class DashboardPage(BasePage):

    h2 = DashboardPageLocators.H2
    sms_templates_link = DashboardPageLocators.SMS_TEMPLATES_LINK
    email_templates_link = DashboardPageLocators.EMAIL_TEMPLATES_LINK
    team_members_link = DashboardPageLocators.TEAM_MEMBERS_LINK
    api_keys_link = DashboardPageLocators.API_KEYS_LINK

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

    def go_to_dashboard_for_service(self, service_id):
        url = "{}/services/{}/dashboard".format(self.base_url, service_id)
        self.driver.get(url)


class SendSmsTemplatePage(BasePage):

    new_sms_template_link = TemplatePageLocators.NEW_TEMPLATE_LINK
    edit_sms_template_link = TemplatePageLocators.EDIT_TEMPLATE_LINK
    send_text_messages_link = TemplatePageLocators.SEND_TEST_MESSAGES_LINK

    def click_add_new_template(self):
        element = self.wait_for_element(SendSmsTemplatePage.new_sms_template_link)
        element.click()

    def click_edit_template(self):
        element = self.wait_for_element(SendSmsTemplatePage.edit_sms_template_link)
        element.click()

    def click_send_from_csv_link(self):
        element = self.wait_for_element(SendSmsTemplatePage.send_text_messages_link)
        element.click()


class EditSmsTemplatePage(BasePage):

    name_input = NameInputElement()
    template_content_input = TemplateContentElement()
    save_button = EditTemplatePageLocators.SAVE_BUTTON

    def click_save(self):
        element = self.wait_for_element(EditSmsTemplatePage.save_button)
        element.click()

    def create_template(self):
        self.name_input = 'Test'
        self.template_content_input = 'The quick brown fox jumped over the lazy dog'
        self.click_save()

    def get_id(self):
        # e.g.
        # http://localhost:6012/services/237dd966-b092-42ab-b406-0a00187d007f/templates/4808eb34-5225-492b-8af2-14b232f05b8e/edit
        # circle back and do better
        return self.driver.current_url.split('/templates/')[1].split('/')[0]


class SendEmailTemplatePage(BasePage):

    new_email_template_link = TemplatePageLocators.NEW_TEMPLATE_LINK
    edit_email_template_link = TemplatePageLocators.EDIT_TEMPLATE_LINK
    send_email_link = TemplatePageLocators.SEND_EMAIL_LINK

    def click_add_new_template(self):
        element = self.wait_for_element(SendEmailTemplatePage.new_email_template_link)
        element.click()

    def click_edit_template(self):
        element = self.wait_for_element(SendEmailTemplatePage.edit_email_template_link)
        element.click()

    def click_send_from_csv_link(self):
        element = self.wait_for_element(SendEmailTemplatePage.send_email_link)
        element.click()


class EditEmailTemplatePage(BasePage):

    name_input = NameInputElement()
    subject_input = SubjectInputElement()
    template_content_input = TemplateContentElement()
    save_button = EditTemplatePageLocators.SAVE_BUTTON

    def click_save(self):
        element = self.wait_for_element(EditEmailTemplatePage.save_button)
        element.click()

    def create_template(self):
        # TODO remove the uuid mularkey once uniqueness of email subject no longer a thing
        import uuid
        self.name_input = 'Test email template'
        self.subject_input = 'Test email from functional tests ' + str(uuid.uuid1())
        self.template_content_input = 'The quick brown fox jumped over the lazy dog'
        self.click_save()

    def get_id(self):
        # e.g.
        # http://localhost:6012/services/237dd966-b092-42ab-b406-0a00187d007f/templates/4808eb34-5225-492b-8af2-14b232f05b8e/edit
        # circle back and do better
        return self.driver.current_url.split('/templates/')[1].split('/')[0]


class UploadCsvPage(BasePage):

    file_input_element = FileInputElement()
    send_button = UploadCsvLocators.SEND_BUTTON

    def click_send(self):
        element = self.wait_for_element(UploadCsvPage.send_button)
        element.click()

    def upload_csv(self, directory, path):
        file_path = os.path.join(directory, 'sample.csv')
        self.file_input_element = file_path
        self.click_send()
        shutil.rmtree(directory, ignore_errors=True)

    def go_to_upload_csv_for_service_and_template(self, service_id, template_id):
        url = "{}/services/{}/send/{}/csv".format(self.base_url, service_id, template_id)
        self.driver.get(url)


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
            element = self.wait_for_element(InviteUserPage.send_messages_checkbox)
            element.click()
        if manage_services:
            element = self.wait_for_element(InviteUserPage.manage_services_checkbox)
            element.click()
        if manage_api_keys:
            element = self.wait_for_element(InviteUserPage.manage_api_keys_checkbox)
            element.click()

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
    create_key_link = ApiKeysPageLocators.CREATE_KEY_LINK
    continue_button = CommonPageLocators.CONTINUE_BUTTON
    api_key_element = ApiKeysPageLocators.API_KEY_ELEMENT

    def enter_key_name(self):
        self.key_name_input = 'Test'

    def click_create_key(self):
        element = self.wait_for_element(ApiKeyPage.create_key_link)
        element.click()

    def click_continue(self):
        element = self.wait_for_element(ApiKeyPage.continue_button)
        element.click()

    def get_api_key(self):
        element = self.wait_for_element(ApiKeyPage.api_key_element)
        return element.text
