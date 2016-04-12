import uuid

from tests.pages.rollups import sign_in

from tests.pages import (
    DashboardPage,
    TeamMembersPage,
    InviteUserPage,
    RegisterFromInvite,
    TwoFactorPage,
    TourPage,
    ProfilePage
)

from tests.utils import (
    get_link,
    generate_unique_email,
    get_verify_code
)

from config import Config


def test_user_can_invite_someone_to_notify(driver, base_url, test_profile):

    sign_in(driver, test_profile)

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_team_members_link()

    team_members_page = TeamMembersPage(driver)
    assert team_members_page.h1_is_team_members()
    team_members_page.click_invite_user()

    invite_user_page = InviteUserPage(driver)

    invited_user_randomness = str(uuid.uuid1())
    invited_user_name = 'Invited User ' + invited_user_randomness
    invite_email = generate_unique_email(Config.FUNCTIONAL_TEST_EMAIL, invited_user_randomness)

    invite_user_page.fill_invitation_form(invite_email, send_messages=True)
    invite_user_page.send_invitation()

    invite_link = get_link(test_profile['email'],
                           test_profile['password'],
                           Config.INVITATION_EMAIL_LABEL)

    invite_user_page.sign_out()

    # next part of interaction is from point of view of invitee
    # i.e. after visting invite_link we'll be registering using invite_email
    # but use same mobile number and password as test_profile

    driver.get(invite_link)
    register_from_invite_page = RegisterFromInvite(driver)
    register_from_invite_page.fill_registration_form(invited_user_name,
                                                     test_profile['mobile'],
                                                     test_profile['password'])
    register_from_invite_page.click_continue()

    two_factor_page = TwoFactorPage(driver)
    verify_code = get_verify_code()
    two_factor_page.verify(verify_code)

    tour_page = TourPage(driver)
    assert tour_page.is_current()
    tour_page.get_me_out_of_here()

    dashboard_page = DashboardPage(driver)
    dashboard_page = DashboardPage(driver)
    assert dashboard_page.is_current()
    assert dashboard_page.h2_is_service_name(test_profile['service_name'])
    dashboard_page.click_user_profile_link(invited_user_name)

    profile_page = ProfilePage(driver)
    assert profile_page.h1_is_correct()
    profile_page.sign_out()
