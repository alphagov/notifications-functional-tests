from operator import attrgetter
from time import sleep
from config import Config
from twilio.rest import TwilioRestClient


def retrieve_sms_with_wait(user_name):
    x = 0
    msgs = get_sms()
    loop_condition = True
    while loop_condition:
        if len(msgs) != 0:
            loop_condition = False
            break
        if x > 12:
            loop_condition = False
            break
        x += 1
        sleep(5)
        msgs = get_sms()

    return sorted(msgs, key=attrgetter('date_created'), reverse=True)


def get_sms():
    client = TwilioRestClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    messages = client.messages.list(to=Config.TWILIO_TEST_NUMBER)
    msgs = []
    if len(messages) > 0:
        msgs = [m for m in messages if m.direction == 'inbound']
    return msgs


def delete_sms_messge(sid):
    from twilio.rest import TwilioRestClient

    client = TwilioRestClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    client.messages.delete(sid)
