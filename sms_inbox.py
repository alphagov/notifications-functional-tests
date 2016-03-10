import os
from flask import Flask, request, jsonify
from flask.ext.cache import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.debug = True


@app.route('/', methods=['GET'])
def get_nessage():
    result = cache.get('sms')
    if result:
        cache.clear()
        return jsonify({
            'result': 'sucess',
            'sms_code': result
        }), 200
    else:
        return jsonify({
            'result': 'error',
            'message': 'no code found'
        }), 404


@app.route('/', methods=['POST'])
def receive_message():
    print(request.values)
    cache.set('sms', request.form['Body'], timeout=300)
    return jsonify({
        'result': 'success'
    }), 200


@app.route('/test-integration', methods=['POST'])
def test_integration():
    print(request.get_data())
    return jsonify({
        'result': 'success'
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6001))	
    app.run(host='0.0.0.0', port=port)
