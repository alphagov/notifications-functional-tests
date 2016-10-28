import os
import uuid
import pytest
from datetime import datetime
from pathlib import Path

from selenium import webdriver

from tests.utils import (
    generate_unique_email
)

from notifications_python_client import NotificationsAPIClient

from tests.pages.rollups import sign_in

from config import Config, PreviewConfig, StagingConfig, LiveConfig


class Profile(object):

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __repr__(self):
        return '{} - {}'.format(self.env, self.email)


@pytest.fixture(scope="session")
def profile():
    env = os.environ['ENVIRONMENT'].lower()

    if env == 'preview':
        uuid_for_test_run = str(uuid.uuid4())
        functional_test_name = PreviewConfig.FUNCTIONAL_TEST_NAME + uuid_for_test_run
        functional_test_email = generate_unique_email(PreviewConfig.FUNCTIONAL_TEST_EMAIL, uuid_for_test_run)
        functional_test_service_name = PreviewConfig.FUNCTIONAL_TEST_SERVICE_NAME + uuid_for_test_run
        functional_test_password = PreviewConfig.FUNCTIONAL_TEST_PASSWORD
        functional_test_mobile = PreviewConfig.TEST_NUMBER
        return Profile(**{'env': PreviewConfig.ENVIRONMENT,
                          'name': functional_test_name,
                          'email': functional_test_email,
                          'service_name': functional_test_service_name,
                          'password': functional_test_password,
                          'mobile': functional_test_mobile,
                          'email_template_id': PreviewConfig.EMAIL_TEMPLATE_ID,
                          'sms_template_id': PreviewConfig.SMS_TEMPLATE_ID,
                          'notify_service_id': PreviewConfig.NOTIFY_SERVICE_ID,
                          'notify_api_url': PreviewConfig.NOTIFY_API_URL,
                          'notify_service_api_key': PreviewConfig.NOTIFY_SERVICE_API_KEY,
                          'notify_research_service_email': PreviewConfig.NOTIFY_RESEARCH_MODE_EMAIL,
                          'notify_research_service_password': PreviewConfig.NOTIFY_RESEARCH_MODE_EMAIL_PASSWORD,
                          'notify_research_service_id': PreviewConfig.NOTIFY_RESEARCH_SERVICE_ID,
                          'notify_research_service_api_key': PreviewConfig.NOTIFY_RESEARCH_SERVICE_API_KEY,
                          'registration_template_id': PreviewConfig.REGISTRATION_TEMPLATE_ID,
                          'invitation_template_id': PreviewConfig.INVITATION_TEMPLATE_ID})
    elif env == 'staging':
        return Profile(**{'env': StagingConfig.ENVIRONMENT,
                          'name': StagingConfig.FUNCTIONAL_TEST_NAME,
                          'email': StagingConfig.FUNCTIONAL_TEST_EMAIL,
                          'service_name': StagingConfig.FUNCTIONAL_TEST_SERVICE_NAME,
                          'password': StagingConfig.FUNCTIONAL_TEST_PASSWORD,
                          'mobile': StagingConfig.TEST_NUMBER,
                          'service_id': StagingConfig.SERVICE_ID,
                          'email_template_id': StagingConfig.EMAIL_TEMPLATE_ID,
                          'sms_template_id': StagingConfig.SMS_TEMPLATE_ID,
                          'api_key': StagingConfig.SERVICE_API_KEY,
                          'notify_api_url': StagingConfig.NOTIFY_API_URL,
                          'registration_template_id': StagingConfig.REGISTRATION_TEMPLATE_ID,
                          'invitation_template_id': StagingConfig.INVITATION_TEMPLATE_ID})
    elif env == 'live':
        return Profile(**{'env': LiveConfig.ENVIRONMENT,
                          'name': LiveConfig.FUNCTIONAL_TEST_NAME,
                          'email': LiveConfig.FUNCTIONAL_TEST_EMAIL,
                          'service_name': LiveConfig.FUNCTIONAL_TEST_SERVICE_NAME,
                          'password': LiveConfig.FUNCTIONAL_TEST_PASSWORD,
                          'mobile': LiveConfig.TEST_NUMBER,
                          'service_id': LiveConfig.SERVICE_ID,
                          'email_template_id': LiveConfig.EMAIL_TEMPLATE_ID,
                          'sms_template_id': LiveConfig.SMS_TEMPLATE_ID,
                          'api_key': LiveConfig.SERVICE_API_KEY,
                          'notify_api_url': LiveConfig.NOTIFY_API_URL,
                          'registration_template_id': LiveConfig.REGISTRATION_TEMPLATE_ID,
                          'invitation_template_id': LiveConfig.INVITATION_TEMPLATE_ID})
    else:
        uuid_for_test_run = str(uuid.uuid4())
        functional_test_name = Config.FUNCTIONAL_TEST_NAME + uuid_for_test_run
        functional_test_email = generate_unique_email(Config.FUNCTIONAL_TEST_EMAIL, uuid_for_test_run)
        functional_test_service_name = Config.FUNCTIONAL_TEST_SERVICE_NAME + uuid_for_test_run
        functional_test_password = Config.FUNCTIONAL_TEST_PASSWORD
        functional_test_email_password = Config.FUNCTIONAL_TEST_EMAIL_PASSWORD
        functional_test_mobile = Config.TEST_NUMBER
        return Profile(**{'env': Config.ENVIRONMENT,
                          'name': functional_test_name,
                          'email': functional_test_email,
                          'service_name': functional_test_service_name,
                          'password': functional_test_password,
                          'mobile': functional_test_mobile,
                          'notify_service_id': Config.NOTIFY_SERVICE_ID,
                          'notify_api_url': Config.NOTIFY_API_URL,
                          'notify_service_api_key': Config.NOTIFY_SERVICE_API_KEY,
                          'registration_template_id': Config.REGISTRATION_TEMPLATE_ID,
                          'invitation_template_id': Config.INVITATION_TEMPLATE_ID})


@pytest.fixture(scope="module")
def _driver():
    driver_name = os.getenv('SELENIUM_DRIVER', 'chrome').lower()
    if os.environ.get('TRAVIS'):
        driver_name = 'firefox'

    if driver_name == 'firefox':
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", "Selenium")
        driver = webdriver.Firefox(profile)
    elif driver_name == 'chrome':
        service_log_path = '/var/project/chromedriver.log'
        service_args = ['--verbose']
        options = webdriver.chrome.options.Options()
        options.add_argument('user-agent=Selenium')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(
            chrome_options=options,
            service_args=service_args,
            service_log_path=service_log_path
        )
    else:
        raise ValueError('Invalid Selenium driver', driver_name)

    driver.delete_all_cookies()
    yield driver
    driver.delete_all_cookies()
    driver.close()


@pytest.fixture(scope='function')
def driver(_driver, request):
    prev_failed_tests = request.session.testsfailed
    yield _driver
    if prev_failed_tests != request.session.testsfailed:
        filename = str(Path.cwd() / 'screenshots' / '{}_{}.png'.format(datetime.utcnow(), request.function.__name__))
        _driver.save_screenshot(str(filename))
        print('Error screenshot saved to ' + filename)


@pytest.fixture(scope="session")
def base_url():
    return Config.NOTIFY_ADMIN_URL


@pytest.fixture(scope="session")
def base_api_url():
    return Config.NOTIFY_API_URL


@pytest.fixture(scope="module")
def login_user(_driver, profile):
    sign_in(_driver, profile)


@pytest.fixture(scope="module")
def login_seeded_user(_driver, profile):
    sign_in(_driver, profile, True)


@pytest.fixture(scope="module")
def client(profile):
    client = NotificationsAPIClient(profile.notify_api_url, profile.service_id, profile.api_key)
    return client


@pytest.fixture(scope="module")
def seeded_client(profile):
    client = NotificationsAPIClient(
        profile.notify_api_url,
        profile.notify_research_service_id,
        profile.notify_research_service_api_key
    )
    return client
