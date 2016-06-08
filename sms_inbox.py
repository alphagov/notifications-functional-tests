import os
from flask import Flask, request, jsonify, abort
from flask.ext.cache import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


def cache_key(prefix):
    return "{}_sms".format(prefix)


@app.route('/')
def index():
    return 'Nothing to see here. Move along.', 200


@app.route('/<environment>', methods=['GET', 'POST'])
def message(environment):
    if request.method == 'GET':
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
    elif request.method == 'POST':
        cache.set(cache_key(environment), request.form['Body'], timeout=300)
        from flask import make_response
        resp = '<?xml version="1.0" encoding="UTF-8" ?><Response />'
        response = make_response(resp)
        response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        return response
    else:
        abort(400)


@app.route('/test-integration', methods=['POST'])
def test_integration():
    return jsonify({
        'result': 'success'
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6001))
    app.run(host='0.0.0.0', port=port)
