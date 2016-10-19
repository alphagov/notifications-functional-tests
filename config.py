import os


class Config(object):
    ENVIRONMENT = os.environ['ENVIRONMENT']
    NOTIFY_ADMIN_URL = os.environ[os.environ['ENVIRONMENT'] + '_NOTIFY_ADMIN_URL']
    NOTIFY_API_URL = os.environ[os.environ['ENVIRONMENT'] + '_NOTIFY_API_URL']
    TEST_NUMBER = os.environ[os.environ['ENVIRONMENT'] + '_TEST_NUMBER']
    FUNCTIONAL_TEST_NAME = os.environ['ENVIRONMENT'] + '_Functional Test_'
    FUNCTIONAL_TEST_EMAIL = os.environ[os.environ['ENVIRONMENT']+'_FUNCTIONAL_TEST_EMAIL']
    FUNCTIONAL_TEST_PASSWORD = os.environ[os.environ['ENVIRONMENT'] + '_FUNCTIONAL_TEST_PASSWORD']
    FUNCTIONAL_TEST_EMAIL_PASSWORD = os.environ[os.environ['ENVIRONMENT'] + '_FUNCTIONAL_TEST_EMAIL_PASSWORD']
    EMAIL_NOTIFICATION_LABEL = 'notify'
    REGISTRATION_EMAIL_LABEL = 'registration'
    INVITATION_EMAIL_LABEL = 'invite'
    EMAIL_TRIES = 36
    EMAIL_DELAY = 5
    RETRY_DELAY = 5
    PROVIDER_RETRY_TIMES = 12
    PROVIDER_RETRY_INTERVAL = 20
    FUNCTIONAL_TEST_SERVICE_NAME = os.environ['ENVIRONMENT'] + '_Functional Test Service_'
    NOTIFY_SERVICE_ID = os.environ[os.environ['ENVIRONMENT'] + '_NOTIFY_SERVICE_ID']
    NOTIFY_SERVICE_API_KEY = os.environ[os.environ['ENVIRONMENT'] + '_NOTIFY_SERVICE_API_KEY']
    REGISTRATION_TEMPLATE_ID = 'ece42649-22a8-4d06-b87f-d52d5d3f0a27'
    INVITATION_TEMPLATE_ID = '4f46df42-f795-4cc4-83bb-65ca312f49cc'
    VERIFY_CODE_TEMPLATE_ID = '36fb0730-6259-4da1-8a80-c8de22ad4246'


class PreviewConfig(Config):
    SMS_TEMPLATE_ID = os.environ.get('preview_SMS_TEMPLATE_ID')
    EMAIL_TEMPLATE_ID = os.environ.get('preview_EMAIL_TEMPLATE_ID')
    NOTIFY_RESEARCH_MODE_EMAIL = os.environ.get('preview_NOTIFY_RESEARCH_MODE_EMAIL')
    NOTIFY_RESEARCH_MODE_EMAIL_PASSWORD = os.environ.get('preview_NOTIFY_RESEARCH_MODE_EMAIL_PASSWORD')
    NOTIFY_RESEARCH_SERVICE_ID = os.environ.get('preview_NOTIFY_RESEARCH_SERVICE_ID')
    NOTIFY_RESEARCH_SERVICE_API_KEY = os.environ.get('preview_NOTIFY_RESEARCH_SERVICE_API_KEY')


class StagingConfig(Config):
    FUNCTIONAL_TEST_SERVICE_NAME = 'Staging FunctionalTest'
    SMS_TEMPLATE_ID = os.environ.get('staging_SMS_TEMPLATE_ID')
    EMAIL_TEMPLATE_ID = os.environ.get('staging_EMAIL_TEMPLATE_ID')
    SERVICE_ID = os.environ.get('staging_SERVICE_ID')
    SERVICE_API_KEY = os.environ.get('staging_API_KEY')


class LiveConfig(Config):
    FUNCTIONAL_TEST_SERVICE_NAME = 'Live FunctionalTest'
    SMS_TEMPLATE_ID = os.environ.get('live_SMS_TEMPLATE_ID')
    EMAIL_TEMPLATE_ID = os.environ.get('live_EMAIL_TEMPLATE_ID')
    SERVICE_ID = os.environ.get('live_SERVICE_ID')
    SERVICE_API_KEY = os.environ.get('live_API_KEY')
