import pytest

from tests.pages import (
    SignInPage,
    TwoFactorPage
)

from tests.utils import get_verify_code


def sign_in(driver, test_profile):
    try:
        sign_in_page = SignInPage(driver)
        sign_in_page.get()
        assert sign_in_page.is_current()
        sign_in_page.login(test_profile['email'], test_profile['password'])
        two_factor_page = TwoFactorPage(driver)
        assert two_factor_page.is_current()
        verify_code = get_verify_code()
        two_factor_page.verify(verify_code)
    except:
        pytest.fail("Unable to log in")
