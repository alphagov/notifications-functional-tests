import hashlib
import os
import tempfile

from filelock import FileLock
from selenium.common.exceptions import TimeoutException

from config import config, generate_unique_email
from tests.pages import SignInPage
from tests.test_utils import do_email_auth_verify, do_verify


def sign_in(driver, account_type="normal", test_name=None):
    lockfile = os.path.join(tempfile.gettempdir(), "signin.lock")
    with FileLock(lockfile):
        _sign_in(driver, account_type, test_name=test_name)
        mobile_number = get_mobile_number(account_type=account_type)
        do_verify(driver, mobile_number)


def sign_in_email_auth(driver):
    _sign_in(driver, "email_auth")
    assert driver.current_url == config["notify_admin_url"] + "/two-factor-email-sent"
    do_email_auth_verify(driver)


def _sign_in(driver, account_type, test_name=None):
    sign_in_page = SignInPage(driver)
    sign_in_page.get()

    try:
        sign_in_page.wait_until_current()
    except TimeoutException:
        # if we didn't get to the sign_in_page, it's probably because we're already logged in.
        # try logging out before proceeding
        sign_in_page.sign_out()
        sign_in_page.get()

    email, password = get_email_and_password(account_type=account_type, test_name=test_name)
    sign_in_page.login(email, password)


def get_email_and_password(account_type, test_name=None):
    if account_type == "normal":
        return config["user"]["email"], config["user"]["password"]
    elif account_type == "seeded":
        if test_name:
            # If the test is parameterised, test_name is eg `test_name[param1, param2]`, which doesn't work
            # for email addresses. Let's strip the parameterisation and generate a short hash to retain uniqueness.
            test_name, _, params = test_name.partition("[")
            if params:
                test_name = test_name + "-" + hashlib.md5(params[:-1].encode()).hexdigest()[:8]

            return (
                generate_unique_email(config["service"]["seeded_user"]["email"], test_name),
                config["service"]["seeded_user"]["password"],
            )

        return (
            config["service"]["seeded_user"]["email"],
            config["service"]["seeded_user"]["password"],
        )
    elif account_type == "email_auth":
        # has the same password as the seeded user
        return (
            config["service"]["email_auth_account"],
            config["service"]["seeded_user"]["password"],
        )
    raise Exception(f"unknown account_type {account_type}")


def get_mobile_number(account_type):
    if account_type == "normal":
        return config["user"]["mobile"]
    elif account_type == "seeded":
        return config["service"]["seeded_user"]["mobile"]
    elif account_type == "email_auth":
        return config["user"]["mobile"]
    raise Exception(f"unknown account_type {account_type}")
