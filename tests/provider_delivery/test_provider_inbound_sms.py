import uuid

from retry.api import retry_call

from config import config


def test_provider_inbound_sms_delivery_via_api(staging_and_prod_client):
    unique_content = "inbound test {}".format(uuid.uuid4())
    staging_and_prod_client.send_sms_notification(
        phone_number=config["service"]["inbound_number"],
        template_id=config["service"]["templates"]["sms"],
        personalisation={"build_id": unique_content},
    )

    retry_call(
        get_inbound_sms,
        fargs=[staging_and_prod_client, unique_content],
        tries=config["provider_retry_times"],
        delay=config["provider_retry_interval"],
    )


def get_inbound_sms(staging_and_prod_client, expected_content):
    # this'll raise if the message isn't in the list.
    return next(
        x
        for x in staging_and_prod_client.get_received_texts()["received_text_messages"]
        if expected_content in x["content"]
    )
