import uuid

from tests.pages import (
    DashboardPage,
    TeamMembersPage,
    InviteUserPage,
    RegisterFromInvite,
    TwoFactorPage,
    TourPage
)

from tests.utils import (
    get_link,
    generate_unique_email,
    get_verify_code
)


def test_user_can_invite_someone_to_notify(driver, base_url, profile, login_user):

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_team_members_link()

    team_members_page = TeamMembersPage(driver)
    assert team_members_page.h1_is_team_members()
    team_members_page.click_invite_user()

    invite_user_page = InviteUserPage(driver)

    invited_user_randomness = str(uuid.uuid1())
    invited_user_name = 'Invited User ' + invited_user_randomness
    invite_email = generate_unique_email(profile['email'], invited_user_randomness)

    invite_user_page.fill_invitation_form(invite_email, send_messages=True)
    invite_user_page.send_invitation()

    invite_link = get_link(profile['email'],
                           profile['email_password'],
                           profile['config'].INVITATION_EMAIL_LABEL)

    invite_user_page.sign_out()

    # next part of interaction is from point of view of invitee
    # i.e. after visting invite_link we'll be registering using invite_email
    # but use same mobile number and password as profile

    driver.get(invite_link)
    register_from_invite_page = RegisterFromInvite(driver)
    register_from_invite_page.fill_registration_form(invited_user_name,
                                                     profile['mobile'],
                                                     profile['password'])
    register_from_invite_page.click_continue()

    two_factor_page = TwoFactorPage(driver)
    verify_code = get_verify_code()
    two_factor_page.verify(verify_code)

    tour_page = TourPage(driver)
    assert tour_page.is_current()
    tour_page.get_me_out_of_here()

    dashboard_page = DashboardPage(driver)
    assert dashboard_page.h2_is_service_name(profile['service_name'])
    dashboard_page.sign_out()
