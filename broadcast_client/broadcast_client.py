import urllib.parse

from notifications_python_client.authentication import create_jwt_token
from notifications_python_client.base import BaseAPIClient


class BroadcastClient(BaseAPIClient):
    def generate_headers(self, api_token):
        return {
            "Content-type": "application/cap+xml",
            "Authorization": f"Bearer {api_token}",
        }

    def _create_request_objects(self, url, data, *args):
        """
        This overwrites `_create_request_objects` in the BaseAPIClient to send the raw data instead of data
        which has been JSON serialized.
        """
        api_token = create_jwt_token(self.api_key, self.service_id)

        kwargs = {
            "headers": self.generate_headers(api_token),
            "timeout": self.timeout,
            "data": data,
        }

        url = urllib.parse.urljoin(self.base_url, url)

        return url, kwargs

    def post_broadcast_data(self, data):
        return self.post("/v2/broadcast", data=data)
