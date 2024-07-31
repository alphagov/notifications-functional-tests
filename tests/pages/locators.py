from selenium.webdriver.common.by import By


class CommonPageLocators(object):
    NAME_INPUT = (By.NAME, "name")
    EMAIL_INPUT = (By.NAME, "email_address")
    PASSWORD_INPUT = (By.NAME, "password")
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "main button.govuk-button")
    ACCEPT_COOKIE_BUTTON = (By.CLASS_NAME, "notify-cookie-banner__button-accept")
    H1 = (By.TAG_NAME, "H1")


class MainPageLocators(object):
    SETUP_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "a.govuk-button.product-page-button")


class SignUpPageLocators(object):
    MOBILE_INPUT = (By.NAME, "mobile_number")


class SignInPageLocators(object):
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgotten your password?")


class NewPasswordPageLocators(object):
    NEW_PASSWORD_INPUT = (By.NAME, "new_password")


class VerifyPageLocators(object):
    SMS_INPUT = (By.NAME, "sms_code")


class AddServicePageLocators(object):
    SERVICE_INPUT = (By.NAME, "name")
    ORG_TYPE_INPUT = (By.ID, "organisation_type-0")
    ADD_SERVICE_BUTTON = (By.CSS_SELECTOR, "main button.govuk-button")


class NavigationLocators(object):
    SIGN_OUT_LINK = (By.LINK_TEXT, "Sign out")
    TEMPLATES_LINK = (By.LINK_TEXT, "Templates")
    SETTINGS_LINK = (By.LINK_TEXT, "Settings")
    PROFILE_LINK = (By.LINK_TEXT, "Your profile")


class TemplatePageLocators(object):
    SEND_TEST_MESSAGES_LINK = (By.LINK_TEXT, "Send text messages")
    SEND_EMAIL_LINK = (By.LINK_TEXT, "Send emails")
    ADD_NEW_TEMPLATE_LINK = (By.LINK_TEXT, "Add new template")
    ADD_A_NEW_TEMPLATE_LINK = (By.LINK_TEXT, "Add a new template")
    EDIT_TEMPLATE_LINK = (By.LINK_TEXT, "Edit template")
    UPLOAD_RECIPIENTS_LINK = (By.LINK_TEXT, "Upload recipients")


class EditTemplatePageLocators(object):
    TEMPLATE_SUBJECT_INPUT = (By.NAME, "subject")
    TEMPLATE_CONTENT_INPUT = (By.NAME, "template_content")
    SAVE_BUTTON = (By.CSS_SELECTOR, "main button.govuk-button")
    DELETE_BUTTON = (By.LINK_TEXT, "Delete this template")
    CONFIRM_DELETE_BUTTON = (By.NAME, "delete")


class RenameTemplatePageLocators(object):
    SAVE_BUTTON = (By.CSS_SELECTOR, "main button.govuk-button")


class ViewLetterTemplatePageLocators(object):
    RENAME_LINK = (By.CLASS_NAME, "folder-heading-manage-link")
    EDIT_BODY = (By.CLASS_NAME, "edit-template-link-letter-body")
    EDIT_WELSH_BODY = (By.XPATH, "//a/span[contains(text(), 'Welsh body')]/..")
    EDIT_ENGLISH_BODY = (By.XPATH, "//a/span[contains(text(), 'English body')]/..")
    ATTACH_BUTTON = (By.CLASS_NAME, "edit-template-link-attachment")
    SEND_BUTTON = (By.CLASS_NAME, "edit-template-link-get-ready-to-send")
    CHANGE_LANGUAGE = (By.LINK_TEXT, "Change language")


class ManageLetterAttachPageLocators(object):
    DELETE_BUTTON = (By.LINK_TEXT, "Remove attachment")
    CONFIRM_DELETE_BUTTON = (By.NAME, "delete")


class UploadCsvLocators(object):
    FILE_INPUT = (By.ID, "file")
    SEND_BUTTON = (
        By.CSS_SELECTOR,
        "form button.govuk-button:not(.govuk-button--secondary)",
    )
    FIRST_NOTIFICATION_AFTER_UPLOAD = (By.CLASS_NAME, "table-row")


class TeamMembersPageLocators(object):
    H1 = (By.TAG_NAME, "h1")
    INVITE_TEAM_MEMBER_BUTTON = (By.CSS_SELECTOR, "a.govuk-button")
    EDIT_TEAM_MEMBER_LINK = (By.LINK_TEXT, "Edit team member")


class InviteUserPageLocators(object):
    SEND_MESSAGES_CHECKBOX = (
        By.CSS_SELECTOR,
        "[value=send_messages], [name=send_messages]",
    )
    SEE_DASHBOARD_CHECKBOX = (
        By.CSS_SELECTOR,
        "[value=view_activity], [name=view_activity]",
    )
    MANAGE_SERVICES_CHECKBOX = (
        By.CSS_SELECTOR,
        "[value=manage_service], [name=manage_service]",
    )
    MANAGE_API_KEYS_CHECKBOX = (
        By.CSS_SELECTOR,
        "[value=manage_api_keys], [name=manage_api_keys]",
    )
    MANAGE_TEMPLATES_CHECKBOX = (
        By.CSS_SELECTOR,
        "[value=manage_templates], [name=manage_templates]",
    )
    CHOOSE_FOLDERS_BUTTON = (
        By.CSS_SELECTOR,
        "button[aria-controls=folder_permissions]",
    )
    SEND_INVITATION_BUTTON = (
        By.CSS_SELECTOR,
        "form button.govuk-button:not(.govuk-button--secondary)",
    )


class ApiIntegrationPageLocators(object):
    MESSAGE_LOG = (By.CSS_SELECTOR, "div.api-notifications details")
    HEADING_BUTTON = (By.CSS_SELECTOR, ".govuk-details__summary")
    CLIENT_REFERENCE = (By.CSS_SELECTOR, ".govuk-details__text .api-notifications-item__data-value:nth-of-type(2)")
    STATUS = (By.CSS_SELECTOR, ".govuk-details__text .api-notifications-item__data-value:last-of-type")
    VIEW_LETTER_LINK = (By.LINK_TEXT, "View letter")


class LetterPreviewPageLocators(object):
    DOWNLOAD_PDF_LINK = (By.LINK_TEXT, "Download as a PDF")
    PDF_IMAGE = (By.CSS_SELECTOR, ".letter img")


class SendLetterPreviewPageLocators(LetterPreviewPageLocators):
    SEND_BUTTON = (By.XPATH, "//button[contains(text(), 'Send 1 letter')]")


class SingleRecipientLocators(object):
    USE_MY_EMAIL = (By.LINK_TEXT, "Use my email address")
    USE_MY_NUMBER = (By.LINK_TEXT, "Use my phone number")
    PLACEHOLDER_NAME = (By.XPATH, "(//label[@for='placeholder_value'])")
    PLACEHOLDER_VALUE_INPUT = (By.NAME, "placeholder_value")
    PREVIEW_TABLE = (By.CLASS_NAME, "email-message-meta")
    ALTERNATIVE_SENDER_RADIO = (By.CSS_SELECTOR, "input[type='radio'][id='sender-1']")
    ALTERNATIVE_SENDER_SMS_RADIO = (
        By.XPATH,
        "//label[normalize-space(text())='func tests']/preceding-sibling::input[@type='radio']",
    )
    ADDRESS_INPUT = (By.ID, "address")
    CONTINUE_BUTTON = (
        By.XPATH,
        "//button[contains(text(),'Continue')]",
    )


class EmailReplyToLocators(object):
    ADD_EMAIL_REPLY_TO_BUTTON = (By.CSS_SELECTOR, "main button.govuk-button")
    CONTINUE_BUTTON = (
        By.XPATH,
        "//a[@class = 'govuk-button' and contains(text(),'Continue')]",
    )
    EMAIL_ADDRESS_FIELD = (By.ID, "email_address")
    REPLY_TO_ADDRESSES = (By.TAG_NAME, "body")
    IS_DEFAULT_CHECKBOX = (By.ID, "is_default")


class SmsSenderLocators(object):
    SMS_SENDER_FIELD = (By.ID, "sms_sender")
    SAVE_SMS_SENDER_BUTTON = (By.CSS_SELECTOR, "main button.govuk-button")
    ALL_SMS_SENDERS = (By.TAG_NAME, "main")
    FIRST_CHANGE_LINK = (By.PARTIAL_LINK_TEXT, "Change")
    SMS_SENDER = (By.CLASS_NAME, "sms-message-sender")
    SMS_RECIPIENT = (By.CLASS_NAME, "sms-message-recipient")
    SMS_CONTENT = (By.CLASS_NAME, "sms-message-wrapper")


class ServiceSettingsLocators(object):
    SERVICE_NAME = (By.CSS_SELECTOR, ".navigation-service-name")
    CHANGE_SERVICE_NAME_LINK = (By.CSS_SELECTOR, ".service-base-settings .govuk-summary-list__row:nth-of-type(1) a")


class ChangeNameLocators(object):
    CHANGE_NAME_FIELD = (By.ID, "name")
    PASSWORD_FIELD = (By.ID, "password")


class ViewTemplatePageLocators(object):
    EDIT_BUTTON = (By.PARTIAL_LINK_TEXT, "Edit")
    SEND_BUTTON = (By.PARTIAL_LINK_TEXT, "Get ready to send")


class UploadAttachmentLocators(object):
    FILE_INPUT = (By.ID, "file")
