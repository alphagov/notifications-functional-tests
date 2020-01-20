from selenium.webdriver.common.by import By


class CommonPageLocators(object):
    NAME_INPUT = (By.NAME, 'name')
    EMAIL_INPUT = (By.NAME, 'email_address')
    PASSWORD_INPUT = (By.NAME, 'password')
    CONTINUE_BUTTON = (By.CLASS_NAME, 'button')
    ACCEPT_COOKIE_BUTTON = (By.CLASS_NAME, 'notify-cookie-banner__button-accept')
    H1 = (By.TAG_NAME, 'H1')


class MainPageLocators(object):
    SETUP_ACCOUNT_BUTTON = (By.CLASS_NAME, 'button')


class SignUpPageLocators(object):
    MOBILE_INPUT = (By.NAME, 'mobile_number')


class VerifyPageLocators(object):
    SMS_INPUT = (By.NAME, 'sms_code')


class AddServicePageLocators(object):
    SERVICE_INPUT = (By.NAME, 'name')
    ORG_TYPE_INPUT = (By.ID, 'organisation_type-0')
    ADD_SERVICE_BUTTON = (By.CLASS_NAME, 'button')


class NavigationLocators(object):
    SIGN_OUT_LINK = (By.LINK_TEXT, 'Sign out')
    TEMPLATES_LINK = (By.LINK_TEXT, 'Templates')
    SETTINGS_LINK = (By.LINK_TEXT, 'Settings')


class TemplatePageLocators(object):
    SEND_TEST_MESSAGES_LINK = (By.LINK_TEXT, 'Send text messages')
    SEND_EMAIL_LINK = (By.LINK_TEXT, 'Send emails')
    ADD_NEW_TEMPLATE_LINK = (By.LINK_TEXT, 'Add new template')
    ADD_A_NEW_TEMPLATE_LINK = (By.LINK_TEXT, 'Add a new template')
    EDIT_TEMPLATE_LINK = (By.LINK_TEXT, 'Edit template')
    UPLOAD_RECIPIENTS_LINK = (By.LINK_TEXT, 'Upload recipients')


class EditTemplatePageLocators(object):
    TEMPLATE_SUBJECT_INPUT = (By.NAME, 'subject')
    TEMPLATE_CONTENT_INPUT = (By.NAME, 'template_content')
    SAVE_BUTTON = (By.CLASS_NAME, 'button')
    DELETE_BUTTON = (By.LINK_TEXT, 'Delete this template')
    CONFIRM_DELETE_BUTTON = (By.NAME, 'delete')


class UploadCsvLocators(object):
    FILE_INPUT = (By.ID, 'file')
    SEND_BUTTON = (By.CSS_SELECTOR, 'main [type=submit]')
    FIRST_NOTIFICATION_AFTER_UPLOAD = (By.CLASS_NAME, 'table-row')


class TeamMembersPageLocators(object):
    H1 = (By.TAG_NAME, 'h1')
    INVITE_TEAM_MEMBER_BUTTON = (By.CLASS_NAME, 'button-secondary')
    EDIT_TEAM_MEMBER_LINK = (By.LINK_TEXT, 'Edit team member')


class InviteUserPageLocators(object):
    SEND_MESSAGES_CHECKBOX = (By.NAME, 'send_messages')
    SEE_DASHBOARD_CHECKBOX = (By.NAME, 'view_activity')
    MANAGE_SERVICES_CHECKBOX = (By.NAME, 'manage_service')
    MANAGE_API_KEYS_CHECKBOX = (By.NAME, 'manage_api_keys')
    MANAGE_TEMPLATES_CHECKBOX = (By.NAME, 'manage_templates')
    CHOOSE_FOLDERS_BUTTON = (By.CSS_SELECTOR, 'button[aria-controls=folder_permissions]')
    SEND_INVITATION_BUTTON = (By.CSS_SELECTOR, 'main [type=submit]')


class ApiIntegrationPageLocators(object):
    MESSAGE_LOG = (By.CSS_SELECTOR, 'div.api-notifications > details:nth-child(1)')
    CLIENT_REFERENCE = (By.CSS_SELECTOR, '.api-notifications-item__data-value')
    MESSAGE_LIST = (By.CSS_SELECTOR, '.api-notifications-item__data-value')
    VIEW_LETTER_LINK = (By.LINK_TEXT, 'View letter')


class LetterPreviewPageLocators(object):
    DOWNLOAD_PDF_LINK = (By.LINK_TEXT, 'Download as a PDF')
    PDF_IMAGE = (By.CSS_SELECTOR, '.letter img')


class ApiKeysPageLocators(object):
    KEY_NAME_INPUT = (By.NAME, 'key_name')
    KEYS_PAGE_LINK = (By.LINK_TEXT, 'API keys')
    CREATE_KEY_LINK = (By.LINK_TEXT, 'Create an API key')
    API_KEY_ELEMENT = (By.XPATH, "(//span[@class='api-key-key'])[last()]")
    NORMAL_KEY_RADIO = (By.XPATH, "//input[@value='normal']")
    TEST_KEY_RADIO = (By.XPATH, "//input[@value='test']")
    TEAM_KEY_RADIO = (By.XPATH, "//input[@value='team']")


class SingleRecipientLocators(object):
    USE_MY_EMAIL = (By.LINK_TEXT, 'Use my email address')
    USE_MY_NUMBER = (By.LINK_TEXT, 'Use my phone number')
    PLACEHOLDER_NAME = (By.XPATH, "(//label[@for='placeholder_value'])")
    PLACEHOLDER_VALUE_INPUT = (By.NAME, 'placeholder_value')
    PREVIEW_TABLE = (By.CLASS_NAME, 'email-message-meta')
    ALTERNATIVE_SENDER_RADIO = (By.CSS_SELECTOR, "input[type='radio'][id='sender-1']")


class EmailReplyToLocators(object):
    ADD_EMAIL_REPLY_TO_BUTTON = (By.CLASS_NAME, 'button')
    CONTINUE_BUTTON = (By.XPATH, "//a[@class = 'button' and contains(text(),'Continue')]")
    EMAIL_ADDRESS_FIELD = (By.ID, 'email_address')
    REPLY_TO_ADDRESSES = (By.TAG_NAME, "body")
    IS_DEFAULT_CHECKBOX = (By.ID, "is_default")


class SmsSenderLocators(object):
    SMS_SENDER_FIELD = (By.ID, 'sms_sender')
    SAVE_SMS_SENDER_BUTTON = (By.CLASS_NAME, 'button')
    ALL_SMS_SENDERS = (By.TAG_NAME, 'main')
    FIRST_CHANGE_LINK = (By.LINK_TEXT, 'Change')
    SMS_SENDER = (By.CLASS_NAME, 'sms-message-sender')
    SMS_RECIPIENT = (By.CLASS_NAME, 'sms-message-recipient')
    SMS_CONTENT = (By.CLASS_NAME, 'sms-message-wrapper')


class ServiceSettingsLocators(object):
    SERVICE_NAME = (By.XPATH, "//div[@class='navigation-service-name']")


class ChangeNameLocators(object):
    CHANGE_NAME_FIELD = (By.ID, 'name')
    PASSWORD_FIELD = (By.ID, 'password')


class ViewTemplatePageLocators(object):
    SEND_BUTTON = (By.LINK_TEXT, 'Send')
