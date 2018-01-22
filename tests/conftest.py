import os
import uuid
import pytest
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from tests.test_utils import (
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

    if env not in ('staging', 'live'):
        # we're running the normal functional tests (whether locally or on preview)
        conf = PreviewConfig if env == 'preview' else Config

        uuid_for_test_run = str(uuid.uuid4())
        functional_test_name = conf.FUNCTIONAL_TEST_NAME + uuid_for_test_run
        functional_test_email = generate_unique_email(conf.FUNCTIONAL_TEST_EMAIL, uuid_for_test_run)
        functional_test_service_name = conf.FUNCTIONAL_TEST_SERVICE_NAME + uuid_for_test_run
        return Profile(**{
            'env': conf.ENVIRONMENT,
            'name': functional_test_name,
            'email': functional_test_email,
            'service_name': functional_test_service_name,
            'password': conf.FUNCTIONAL_TEST_PASSWORD,
            'mobile': conf.TEST_NUMBER,
            'jenkins_build_email_template_id': conf.JENKINS_BUILD_EMAIL_TEMPLATE_ID,
            'jenkins_build_sms_template_id': conf.JENKINS_BUILD_SMS_TEMPLATE_ID,
            'jenkins_build_letter_template_id': conf.JENKINS_BUILD_LETTER_TEMPLATE_ID,
            'notify_api_url': conf.NOTIFY_API_URL,
            'notify_service_api_key': conf.NOTIFY_SERVICE_API_KEY,
            'notify_research_service_email': conf.NOTIFY_RESEARCH_MODE_EMAIL,
            'notify_research_service_password': conf.NOTIFY_RESEARCH_MODE_EMAIL_PASSWORD,
            'notify_research_service_id': conf.NOTIFY_RESEARCH_SERVICE_ID,
            'notify_research_service_api_key': conf.NOTIFY_RESEARCH_SERVICE_API_KEY,
            'notify_research_service_name': conf.NOTIFY_RESEARCH_SERVICE_NAME,
            'notify_research_sms_sender': conf.NOTIFY_RESEARCH_SMS_SENDER,
            'notify_research_email_reply_to': conf.NOTIFY_RESEARCH_EMAIL_REPLY_TO,
            'notify_research_letter_contact': conf.NOTIFY_RESEARCH_LETTER_CONTACT,
            'registration_template_id': conf.REGISTRATION_TEMPLATE_ID,
            'invitation_template_id': conf.INVITATION_TEMPLATE_ID,
            'email_auth_template_id': conf.EMAIL_AUTH_TEMPLATE_ID,
            'notify_research_service_email_auth_account': conf.NOTIFY_RESEARCH_SERVICE_EMAIL_AUTH_ACCOUNT
        })
    else:
        # staging and live run the same simple smoke tests
        if env == 'staging':
            conf = StagingConfig
        if env == 'live':
            conf = LiveConfig
        return Profile(**{
            'env': conf.ENVIRONMENT,
            'name': conf.FUNCTIONAL_TEST_NAME,
            'email': conf.FUNCTIONAL_TEST_EMAIL,
            'service_name': conf.FUNCTIONAL_TEST_SERVICE_NAME,
            'password': conf.FUNCTIONAL_TEST_PASSWORD,
            'mobile': conf.TEST_NUMBER,
            'service_id': conf.SERVICE_ID,
            'jenkins_build_email_template_id': conf.JENKINS_BUILD_EMAIL_TEMPLATE_ID,
            'jenkins_build_sms_template_id': conf.JENKINS_BUILD_SMS_TEMPLATE_ID,
            'api_key': conf.SERVICE_API_KEY,
            'notify_api_url': conf.NOTIFY_API_URL,
        })


@pytest.fixture(scope="module")
def _driver():
    driver_name = (os.getenv('SELENIUM_DRIVER') or 'chrome').lower()
    if os.environ.get('TRAVIS'):
        driver_name = 'firefox'

    http_proxy = os.getenv('HTTP_PROXY')

    if driver_name == 'firefox':
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", "Selenium")

        if http_proxy is not None and http_proxy != "":
            http_proxy_url = http_proxy.split(':')[0] + ':' + http_proxy.split(':')[1]
            http_proxy_port = int(http_proxy.split(':')[2])
            profile.set_preference("network.proxy.type", 5)
            profile.set_preference("network.proxy.http", http_proxy_url)
            profile.set_preference("network.proxy.http_port", http_proxy_port)
            profile.set_preference("network.proxy.https", http_proxy_url)
            profile.set_preference("network.proxy.https_port", http_proxy_port)
            profile.set_preference("network.proxy.ssl", http_proxy_url)
            profile.set_preference("network.proxy.ssl_port", http_proxy_port)
            profile.update_preferences()

        binary = FirefoxBinary(log_file=open("./logs/browser.log", "wb"))
        driver = webdriver.Firefox(profile, firefox_binary=binary)
        driver.set_window_position(0, 0)
        driver.set_window_size(1280, 720)

    elif driver_name == 'chrome':
        options = webdriver.chrome.options.Options()
        service_args = ['--verbose']
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Selenium")

        if http_proxy is not None and http_proxy != "":
            options.add_argument('--proxy-server={}'.format(http_proxy))

        driver = webdriver.Chrome(service_log_path='./logs/chrome_browser.log',
                                  service_args=service_args,
                                  chrome_options=options)

    elif driver_name == 'phantomjs':

        service_args = None

        if http_proxy is not None and http_proxy != "":
            service_args = [
                '--proxy={}'.format(http_proxy)
            ]

        driver = webdriver.PhantomJS(service_args=service_args,
                                     service_log_path='./logs/phantomjs.log')
        driver.maximize_window()

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
    client = NotificationsAPIClient(
        base_url=profile.notify_api_url,
        api_key=profile.api_key
    )
    return client


@pytest.fixture(scope="module")
def seeded_client(profile):
    client = NotificationsAPIClient(
        base_url=profile.notify_api_url,
        api_key=profile.notify_research_service_api_key
    )
    return client
