import uuid
from datetime import datetime
from pathlib import Path

import pytest
from notifications_python_client import NotificationsAPIClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.events import EventFiringWebDriver

from config import config, setup_shared_config
from tests.event_listener import LoggingEventListener
from tests.pages.pages import HomePage
from tests.pages.rollups import sign_in, sign_in_email_auth


def pytest_addoption(parser):
    parser.addoption("--no-headless", action="store_true", default=False)
    parser.addoption("--unique-screenshot-filenames", action="store_true", default=False)
    parser.addoption("--unique-domdump-filenames", action="store_true", default=False)


@pytest.fixture(scope="session", autouse=True)
def shared_config():
    """
    Setup shared config variables (eg env and urls)
    """
    setup_shared_config()


@pytest.fixture(scope="session")
def download_directory(tmp_path_factory):
    return tmp_path_factory.mktemp("downloads")


@pytest.fixture(scope="module")
def _driver(request, download_directory):
    driver_id = uuid.uuid4()

    options = webdriver.chrome.options.Options()
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-agent=Selenium/driver-{driver_id}")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(download_directory),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
        },
    )

    if not request.config.getoption("--no-headless"):
        options.add_argument("--headless")

    service = ChromeService(log_path=f"./logs/chrome_browser.{driver_id}.log", service_args=["--verbose"])

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1280, 1200)

    driver = EventFiringWebDriver(driver, LoggingEventListener())
    driver._listener.set_node(request.node.name)
    driver._driver_id = driver_id

    driver.delete_all_cookies()

    # go to root page and accept analytics cookies to hide banner in all pages
    driver.get(config["notify_admin_url"])
    HomePage(driver).accept_cookie_warning()

    yield driver
    driver.delete_all_cookies()
    driver.close()


@pytest.fixture(scope="function")
def driver(_driver, request):
    prev_failed_tests = request.session.testsfailed
    _driver._listener.set_node(request.node.name)
    yield _driver
    if prev_failed_tests != request.session.testsfailed:
        print("driver_id:", getattr(_driver, "_driver_id", None))  # noqa: T201
        print("URL at time of failure:", datetime.now().isoformat(), _driver.current_url)  # noqa: T201

        # print last 20 events
        _driver._listener.print_events(node=request.node.name, num_to_print=20)

        unique_filename_base = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_{request.function.__name__}"

        screenshot_filename = (
            unique_filename_base if request.config.getoption("--unique-screenshot-filenames") else "test_failure"
        ) + ".png"
        screenshot_path = Path.cwd() / "screenshots" / screenshot_filename

        _driver.save_screenshot(str(screenshot_path))
        print("Error screenshot saved to ", screenshot_path)  # noqa: T201

        domdump_filename = (
            unique_filename_base if request.config.getoption("--unique-domdump-filenames") else "test_failure"
        ) + ".dom.html"
        domdump_dir = Path.cwd() / "domdumps"
        domdump_dir.mkdir(parents=True, exist_ok=True)
        domdump_path = domdump_dir / domdump_filename

        with open(domdump_path, "w") as f:
            f.write(_driver.execute_script("return document.documentElement.outerHTML"))

        print("DOM dump saved to ", domdump_path)  # noqa: T201

    # clear old events/urls regardless of failure
    _driver._listener.clear_events()


@pytest.fixture(scope="module")
def login_user(_driver):
    sign_in_email_auth(_driver)


@pytest.fixture(scope="function")
def login_seeded_user(_driver, request: pytest.FixtureRequest):
    _driver.delete_all_cookies()
    sign_in(_driver, account_type="seeded", test_name=request.node.name)


@pytest.fixture(scope="module")
def client_live_key():
    client = NotificationsAPIClient(base_url=config["notify_api_url"], api_key=config["service"]["api_live_key"])
    return client


@pytest.fixture(scope="module")
def client_test_key():
    client = NotificationsAPIClient(base_url=config["notify_api_url"], api_key=config["service"]["api_test_key"])
    return client
