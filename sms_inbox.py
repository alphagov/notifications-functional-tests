import os
from flask import Flask, request, jsonify, json
from flask.ext.cache import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.debug = True


def create_key(prefix):
    return "{}_sms".format(prefix)


@app.route('/<environment>', methods=['GET'])
def get_message(environment):
    result = cache.get(cache_key(environment))
    if result:
        cache.delete(cache_key(environment))
        return jsonify({
            'result': 'success',
            'sms_code': result
        }), 200
    else:
        return jsonify({
            'result': 'error',
            'message': 'no code found'
        }), 404


@app.route('/<environment>', methods=['POST'])
def receive_message(environment):
    cache.set(cache_key(environment), request.form['Body'], timeout=300)
    return "OK", 200


@app.route('/test-integration', methods=['POST'])
def test_integration():
    return jsonify({
        'result': 'success'
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6001))
    app.run(host='0.0.0.0', port=port)
