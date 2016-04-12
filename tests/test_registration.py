from config import Config

from tests.utils import (
    get_link,
    get_verify_code
)

from tests.pages import (
    MainPage,
    RegistrationPage,
    VerifyPage,
    DashboardPage,
    AddServicePage,
    TourPage
)


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

    registration_link = get_link(test_profile['email'],
                                 test_profile['password'],
                                 Config.REGISTRATION_EMAIL_LABEL)
    driver.get(registration_link)
    verify_code = get_verify_code()

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
    # dashboard_page.sign_out()
