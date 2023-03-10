from flask import Flask, jsonify, request, render_template, redirect

app = Flask(__name__)


@app.before_request
def before_request():
    if request.is_secure:
        url = request.url.replace('https://', 'http://', 1)
        code = 301
        return redirect(url, code=code)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, debug=True,
            ssl_context=('cert.pem', 'key.pem'))
