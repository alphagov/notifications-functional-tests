"""

Fixture:
    hand-craft a request to POST to the receive messages API (mocking out the provider)

Test:
    use API to get inbound messages - assert that the new message is in the response

Test:
    look at inbox page - assert that the new message is in the conversation
"""

from datetime import datetime
from urllib.parse import quote_plus

import pytest
import requests
from retry import retry

from config import config
from tests.pages import ConversationPage, DashboardPage, InboxPage


@pytest.fixture(scope="module")
def inbound_sms():
    # the message has the func test user's name in it - which has a unique uuid
    message = "Inbound message from {}".format(config["user"]["name"])

    # hand-craft a request to receive messages API.
    mmg_inbound_body = {
        "MSISDN": config["user"]["mobile"],  # from_user number
        "Number": config["service"]["inbound_number"],  # service inbound number
        "Message": quote_plus(message),
        "ID": "SOME-MMG-SPECIFIC-ID",
        "DateRecieved": quote_plus(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
    }

    response = requests.post(
        config["notify_api_url"] + "/notifications/sms/receive/mmg",
        json=mmg_inbound_body,
        auth=(
            config["mmg_inbound_sms"]["username"],
            config["mmg_inbound_sms"]["password"],
        ),
    )
    response.raise_for_status()

    return message


@pytest.mark.xdist_group(name="api-client")
def test_inbound_api(inbound_sms, client_live_key):
    # this'll raise if the message isn't in the list.
    next(x for x in client_live_key.get_received_texts()["received_text_messages"] if x["content"] == inbound_sms)


@retry(
    AssertionError,
    tries=config["verify_callback_retry_times"],
    delay=config["verify_callback_retry_interval"],
)
def assert_callback_received(inbound_sms):
    source_id = config["pipedream"]["source_id"]
    api_token = config["pipedream"]["api_token"]

    response = requests.get(
        f"https://api.pipedream.com/v1/sources/{source_id}/event_summaries?expand=event&limit=10",
        headers={"Authorization": f"Bearer {api_token}"},
    )

    response.raise_for_status()

    recent_callback_requests = [item["event"] for item in response.json()["data"]]
    matching_callback_requests = [
        request for request in recent_callback_requests if request.get("body", {}).get("message") == inbound_sms
    ]

    assert len(matching_callback_requests) == 1


def test_inbound_sms_callbacks(inbound_sms):
    assert_callback_received(inbound_sms)


def test_inbox_page(inbound_sms, driver, login_seeded_user):
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config["service"]["id"])

    # go to inbox page
    dashboard_page.click_inbox_link()

    # select conversation for outbound phone number
    inbox_page = InboxPage(driver)
    assert inbox_page.is_current(config["service"]["id"])

    inbox_page.go_to_conversation(config["user"]["mobile"])

    conversation = ConversationPage(driver)
    assert conversation.get_message(inbound_sms) is not None
