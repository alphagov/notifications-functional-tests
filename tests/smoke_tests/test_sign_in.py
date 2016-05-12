import pytest

from tests.pages import (
    SignInPage,
    TwoFactorPage,
    DashboardPage
)

from tests.utils import (
    get_verify_code,
    send_to_deskpro
)


def test_sign_in(driver, base_url, profile):
    try:
        sign_in_page = SignInPage(driver)
        sign_in_page.get()
        assert sign_in_page.is_current()
        sign_in_page.login(profile['email'], profile['password'])

        two_factor_page = TwoFactorPage(driver)
        assert two_factor_page.is_current()

        verify_code = get_verify_code()
        two_factor_page.verify(verify_code)

        dashboard_page = DashboardPage(driver)

        assert dashboard_page.is_current(profile['config'].SERVICE_ID)
        dashboard_page.sign_out()
    except Exception as e:
        message = "Test failure in sign in test for {}. Exception: {}".format(profile['config'].NOTIFY_ADMIN_URL, e)
        send_to_deskpro(profile['config'], message)
        pytest.fail("This is something not good")
