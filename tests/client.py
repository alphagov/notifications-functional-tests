import os

from notifications_python_client import NotificationsAPIClient


# This allows us to set an additional HTTP header with every HTTP request
# made by our python Notify API client. This extra header can be
# toggled on and if based on the NOTIFY_ECS_ORIGIN environment variable
# and will send requests to our ECS infrastructure instead of our PaaS
# infrastructure by using the special header required by our Lambda function
# https://github.com/alphagov/notifications-aws/tree/main/terraform/modules/migrate-traffic-to-ecs-lambda
def ecs_override_generate_headers(self, api_token):
    headers = self.original_generate_headers(api_token)
    if os.getenv("NOTIFY_ECS_ORIGIN"):
        headers["x-notify-ecs-origin"] = "true"
    return headers


FunctionalTestsAPIClient = NotificationsAPIClient
FunctionalTestsAPIClient.original_generate_headers = (
    FunctionalTestsAPIClient.generate_headers
)
FunctionalTestsAPIClient.generate_headers = ecs_override_generate_headers
