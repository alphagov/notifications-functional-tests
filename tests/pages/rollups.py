from config import config
from tests.pages import SignInPage

from tests.test_utils import do_verify, do_email_auth_verify


def sign_in(driver, seeded=False):
    _sign_in(driver, 'seeded' if seeded else 'normal')
    do_verify(driver)


def sign_in_email_auth(driver):
    _sign_in(driver, 'email_auth')
    assert driver.current_url == config['notify_admin_url'] + '/two-factor-email-sent'
    do_email_auth_verify(driver)


def _sign_in(driver, account_type):
    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    assert sign_in_page.is_current()
    email, password = _get_email_and_password(account_type=account_type)
    sign_in_page.login(email, password)


def _get_email_and_password(account_type):
    if account_type == 'normal':
        return config['user']['email'], config['user']['password']
    elif account_type == 'seeded':
        return config['service']['seeded_user']['email'], config['service']['seeded_user']['password']
    elif account_type == 'email_auth':
        # has the same password as the seeded user
        return config['service']['email_auth_account'], config['service']['seeded_user']['password']
    raise Exception('unknown account_type {}'.format(account_type))
