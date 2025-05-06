import os
from flask import Flask, redirect, url_for, current_app
from flask_wtf.csrf import CSRFError
from election1 import create_app

app: Flask = create_app()


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return redirect(url_for('mains.homepage'))  # Redirect to the login page


if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    host = os.getenv('URL_HOST', '127.0.0.1')  # Default to '127.0.0.1'
    port = os.getenv('URL_PORT', '5000')
    app.run(host=host, port=int(port), debug=True)