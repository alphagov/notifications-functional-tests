import pytest

from config import Config

from tests.utils import (
    get_email_body,
    remove_all_emails,
    get_sms_via_heroku
)

from tests.pages import (
    MainPage,
    RegistrationPage,
    VerifyPage,
    DashboardPage,
    AddServicePage,
    TourPage
)


# TODO maybe move these to utils
def _get_registration_link():
    import re

    try:
        email_body = get_email_body(Config.FUNCTIONAL_TEST_EMAIL,
                                    Config.FUNCTIONAL_TEST_PASSWORD,
                                    Config.REGISTRATION_EMAIL_LABEL)
        match = re.search('http[s]?://\S+', email_body)
        if match:
            return match.group(0)
        else:
            pytest.fail("Couldn't get the registraion link from the email")
    finally:
        remove_all_emails(email_folder=Config.REGISTRATION_EMAIL_LABEL)


def _get_verify_code():
    from requests import session
    verify_code = get_sms_via_heroku(session())
    if not verify_code:
        pytest.fail("Could not get the verify code")
    return verify_code

# end utils to move


def test_user_registration(driver, base_url, test_profile):

    main_page = MainPage(driver)
    main_page.get()
    main_page.click_set_up_account()

    registration_page = RegistrationPage(driver)
    assert registration_page.is_current()

    registration_page.register(test_profile['name'],
                               test_profile['email'],
                               test_profile['mobile'],
                               test_profile['password'])

    assert driver.current_url == base_url + '/registration-continue'

    registration_link = _get_registration_link()
    driver.get(registration_link)
    verify_code = _get_verify_code()

    verify_page = VerifyPage(driver)
    assert verify_page.is_current()
    verify_page.verify(verify_code)

    add_service_page = AddServicePage(driver)
    assert add_service_page.is_current()
    add_service_page.add_service(test_profile['service_name'])

    tour_page = TourPage(driver)
    assert tour_page.is_current()
    tour_page.get_me_out_of_here()

    dashboard_page = DashboardPage(driver)
    assert dashboard_page.is_current()
    assert dashboard_page.h2_is_service_name(test_profile['service_name'])
    dashboard_page.sign_out()
