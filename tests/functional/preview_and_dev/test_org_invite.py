import uuid

from config import config, generate_unique_email
from tests.pages import (
    DashboardPage,
    InviteUserToOrgPage,
    OrganisationDashboardPage,
    RegisterFromInvite,
    TeamMembersPage,
)
from tests.test_utils import do_verify, get_link, recordtime


@recordtime
def test_org_invite(driver, login_seeded_user):
    org_dashboard_page = OrganisationDashboardPage(driver)
    org_dashboard_page.go_to_dashboard_for_org(config["service"]["organisation_id"])
    assert org_dashboard_page.is_current(config["service"]["organisation_id"])
    org_dashboard_page.click_team_members_link()

    team_members_page = TeamMembersPage(driver)
    team_members_page.click_invite_user()

    # create a new user to log in to
    invited_user_email = generate_unique_email(config["user"]["email"], uuid.uuid4())

    invitation = InviteUserToOrgPage(driver)
    invitation.fill_invitation_form(email=invited_user_email)
    invitation.send_invitation()

    # now log out and create account as invited user
    dashboard_page = DashboardPage(driver)
    dashboard_page.sign_out()
    dashboard_page.wait_until_url_is(config["notify_admin_url"])

    invite_link = get_link(config["notify_templates"]["org_invitation_template_id"], invited_user_email)
    driver.get(invite_link)

    register_from_invite_page = RegisterFromInvite(driver)
    register_from_invite_page.fill_registration_form(invited_user_email.split("@")[0])
    register_from_invite_page.click_continue()

    do_verify(driver, config["user"]["mobile"])

    org_dashboard_page = OrganisationDashboardPage(driver)

    # make sure we got to the dashboard page. It's their only account, so they'll be insta-redirected there.
    # They won't be able to see anything here tho since they're not a member of the service
    assert org_dashboard_page.is_current(config["service"]["organisation_id"])
