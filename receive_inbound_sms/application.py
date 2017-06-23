import os

from flask import Flask, jsonify
from flask import request

app = Flask(__name__)

bearer_token = os.environ['BEARER_TOKEN']


@app.route('/inbound-sms/from-notify', methods=['POST'])
def inbound_sms_from_notify():
    auth_header = request.headers.get('Authorization', None)
    if auth_header == "Bearer {}".format(bearer_token):
        data = request.get_json()
        return jsonify(message=data), 200
    else:
        return jsonify(error="Bearer token is invalid"), 403


@app.route('/inbound-sms/from-notify/exception')
def inbound_sms_exception():
    return jsonify(error="Didn't get it"), 400


if __name__ == "__main__":
    app.run(ssl_context='adhoc')