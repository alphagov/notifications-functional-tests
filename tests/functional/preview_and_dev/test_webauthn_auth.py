
from config import config
from tests.pages import (
    BasePage,
)
from tests.pages.rollups import sign_in_webauthn
from tests.test_utils import recordtime


@recordtime
def test_webauthn_auth(driver):
    sign_in_webauthn(driver, account_type='broadcast_create_user')

    # assert url is FUNCTIONAL_TESTS_SERVICE's dashboard
    assert driver.current_url == config['notify_admin_url'] + '/services/{}'.format(config['service']['id'])

    base_page = BasePage(driver)
    base_page.sign_out()
