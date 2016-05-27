from tests.utils import (
    get_link,
    get_verify_code
)

from tests.pages import (
    MainPage,
    RegistrationPage,
    VerifyPage,
    DashboardPage,
    AddServicePage
)


def test_user_registration(driver, base_url, profile):

    main_page = MainPage(driver)
    main_page.get()
    main_page.click_set_up_account()

    registration_page = RegistrationPage(driver)
    assert registration_page.is_current()

    registration_page.register(profile)

    assert driver.current_url == base_url + '/registration-continue'

    registration_link = get_link(profile, profile.registration_email_label)

    driver.get(registration_link)
    verify_code = get_verify_code()

    verify_page = VerifyPage(driver)
    assert verify_page.is_current()
    verify_page.verify(verify_code)

    add_service_page = AddServicePage(driver)
    assert add_service_page.is_current()
    add_service_page.add_service(profile.service_name)

    dashboard_page = DashboardPage(driver)
    service_id = dashboard_page.get_service_id()
    dashboard_page.go_to_dashboard_for_service(service_id)

    assert dashboard_page.h2_is_service_name(profile.service_name)
    dashboard_page.sign_out()
