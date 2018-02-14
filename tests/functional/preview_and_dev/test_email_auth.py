from tests.test_utils import recordtime

from tests.pages.rollups import sign_in_email_auth


@recordtime
def test_email_auth(driver, profile, base_url):
    # login email auth user
    sign_in_email_auth(driver, profile)
    # assert url is research mode service's dashboard
    assert (
        driver.current_url == base_url + '/services/{}/dashboard'.format(profile.notify_research_service_id)
    ) or (
        driver.current_url == base_url + '/services/{}'.format(profile.notify_research_service_id)
    )
