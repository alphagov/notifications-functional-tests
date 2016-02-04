from operator import attrgetter
from time import sleep

from config import Config
from twilio.rest import TwilioRestClient


def retrieve_sms(user_name):
    sleep(5)
    client = TwilioRestClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

    x = 1
    messages = client.messages.list(to="+44 1509 323441")
    while x < 12 and len(messages) == 0:
        print("In loop {} times".format(x))
        for m in messages:
            print("verify code: {}".format(m.body))
            break
        x += 1
        sleep(5)
        messages = client.messages.list(to=Config.TWILIO_TEST_NUMBER)

    msgs = [m for m in messages if m.direction== 'inbound']
    assert len(msgs) > 0, 'No sms retrieved for functional test for user: {}'.format(user_name)
    return sorted(msgs, key=attrgetter('date_created'), reverse=True)


def delete_sms_messge(sid):
    from twilio.rest import TwilioRestClient

    client = TwilioRestClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    client.messages.delete(sid)