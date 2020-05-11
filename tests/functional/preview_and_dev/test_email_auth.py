from config import config
from tests.test_utils import do_email_verification, recordtime

from tests.pages.rollups import sign_in_email_auth
from tests.pages import BasePage, ForgotPasswordPage, NewPasswordPage, SignInPage
from tests.pages.rollups import get_email_and_password


@recordtime
def test_email_auth(driver):
    # login email auth user
    sign_in_email_auth(driver)
    # assert url is FUNCTIONAL_TESTS_SERVICE's dashboard
    assert driver.current_url == config['notify_admin_url'] + '/services/{}'.format(config['service']['id'])
    base_page = BasePage(driver)
    base_page.sign_out()


@recordtime
def test_reset_forgotten_password(driver):
    email, password = get_email_and_password(account_type='seeded')
    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    assert sign_in_page.is_current()
    sign_in_page.click_forgot_password_link()

    forgot_password_page = ForgotPasswordPage(driver)
    assert forgot_password_page.is_page_title("Forgotten your password?")
    forgot_password_page.input_email_address(email)
    forgot_password_page.click_continue()
    assert forgot_password_page.is_page_title("Check your email")

    do_email_verification(
        driver,
        config['notify_templates']['password_reset_template_id'],
        email
    )
    new_password_page = NewPasswordPage(driver)
    assert new_password_page.is_page_title("Create a new password")
    new_password_page.input_new_password(password)
    new_password_page.click_continue()

    assert new_password_page.is_page_title("Check your phone")
