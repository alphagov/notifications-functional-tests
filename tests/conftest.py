import os
from datetime import datetime
from pathlib import Path

import pytest
from notifications_python_client import NotificationsAPIClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

from config import config, setup_shared_config
from tests.pages.pages import HomePage
from tests.pages.rollups import sign_in_sms, sign_in_email_auth


@pytest.fixture(scope="session", autouse=True)
def shared_config():
    """
    Setup shared config variables (eg env and urls)
    """
    setup_shared_config()


@pytest.fixture(scope="module")
def _driver():
    http_proxy = os.getenv('HTTP_PROXY')

    options = webdriver.chrome.options.Options()
    options.add_argument("--no-sandbox")
    # options.add_argument("--headless")
    options.add_argument("user-agent=Selenium")

    if http_proxy is not None and http_proxy != "":
        options.add_argument('--proxy-server={}'.format(http_proxy))

    service = ChromeService(log_path='./logs/chrome_browser.log', service_args=['--verbose'])

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1280, 720)

    driver.delete_all_cookies()

    # go to root page and accept analytics cookies to hide banner in all pages
    driver.get(config['notify_admin_url'])
    HomePage(driver).accept_cookie_warning()
    yield driver
    driver.delete_all_cookies()
    driver.close()


@pytest.fixture(scope='function')
def driver(_driver, request):
    prev_failed_tests = request.session.testsfailed
    yield _driver
    if prev_failed_tests != request.session.testsfailed:
        print('URL at time of failure:', _driver.current_url)
        filename_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = str(Path.cwd() / 'screenshots' / '{}_{}.png'.format(filename_datetime, request.function.__name__))
        _driver.save_screenshot(str(filename))
        print('Error screenshot saved to ' + filename)


@pytest.fixture(scope="module")
def login_user(_driver):
    sign_in_email_auth(_driver)


@pytest.fixture(scope="module")
def login_seeded_user(_driver):
    sign_in_sms(_driver, account_type='seeded')


@pytest.fixture(scope="module")
def client():
    client = NotificationsAPIClient(
        base_url=config['notify_api_url'],
        api_key=config['service']['api_key']
    )
    return client


@pytest.fixture(scope="module")
def seeded_client():
    client = NotificationsAPIClient(
        base_url=config['notify_api_url'],
        api_key=config['service']['api_live_key']
    )
    return client


@pytest.fixture(scope="module")
def seeded_client_using_test_key():
    client = NotificationsAPIClient(
        base_url=config['notify_api_url'],
        api_key=config['service']['api_test_key']
    )
    return client
