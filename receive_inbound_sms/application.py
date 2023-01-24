import os

from flask import Flask, jsonify, request

app = Flask(__name__)

bearer_token = os.environ["BEARER_TOKEN"]
port = int(os.environ.get("PORT", 6014))


@app.route("/inbound-sms/from-notify", methods=["POST"])
def inbound_sms_from_notify():
    auth_header = request.headers.get("Authorization", None)
    if auth_header == "Bearer {}".format(bearer_token):
        data = request.get_json()
        return jsonify(message=data), 200
    else:
        return jsonify(error="Bearer token is invalid"), 403


@app.route("/inbound-sms/from-notify/exception")
def inbound_sms_exception():
    return jsonify(error="Didn't get it"), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, ssl_context="adhoc")
