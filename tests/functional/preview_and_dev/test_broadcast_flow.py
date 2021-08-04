import uuid

from config import config
from tests.pages import DashboardPage
from tests.pages.rollups import sign_in_broadcast_user
from tests.test_utils import (
    create_broadcast_template,
    delete_template,
    go_to_templates_page,
    recordtime,
)


@recordtime
def test_prepare_broadcast_with_template(
    driver, seeded_client
):
    sign_in_broadcast_user(driver)

    go_to_templates_page(driver, service='broadcast_service')
    template_name = "test broadcast" + str(uuid.uuid4())
    content = "This is a test only."
    create_broadcast_template(driver, name=template_name, content=content)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config['broadcast_service']['id'])

    delete_template(driver, template_name, service='broadcast_service')

    """
    check you're on broadcast page dashboard
    go to templates
    create a new broadcast template
    click `get ready to send`
    click `test areas`
    click A and B
    Check that the header is "Choose where to send this alert"
    Check that there are 2 "area-list-item" items, and they correspond to selected areas
    Click "Preview this alert"
    Check that content is the content from the template and areas are selected areas
    Click ""Submit for approval"
    Check that you can see " {template_name} is waiting for approval" text
    """
