from config import config
from tests.test_utils import recordtime

from tests.pages.rollups import sign_in_email_auth


@recordtime
def test_email_auth(driver):
    # login email auth user
    sign_in_email_auth(driver)
    # assert url is research mode service's dashboard
    assert driver.current_url == config['notify_admin_url'] + '/services/{}'.format(config['service']['id'])
