import uuid

from retry.api import retry_call

from config import config


def test_provider_inbound_sms_delivery_via_api(client_live_key):
    unique_content = f"inbound test {uuid.uuid4()}"
    client_live_key.send_sms_notification(
        phone_number=config["service"]["inbound_number"],
        template_id=config["service"]["templates"]["sms"],
        personalisation={"name": "Testy McTesterson", "content": unique_content},
    )

    retry_call(
        get_inbound_sms,
        fargs=[client_live_key, unique_content],
        tries=config["provider_retry_times"],
        delay=config["provider_retry_interval"],
    )


def get_inbound_sms(client_live_key, expected_content):
    # this'll raise if the message isn't in the list.
    return next(
        x for x in client_live_key.get_received_texts()["received_text_messages"] if expected_content in x["content"]
    )
