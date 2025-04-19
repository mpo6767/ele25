import os
from flask import Flask, redirect, url_for
from flask_wtf.csrf import CSRFError
from election1 import create_app

app: Flask = create_app()


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return redirect(url_for('mains.homepage'))  # Redirect to the login page


if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    app.run(host="0.0.0.0",port=5000,debug=True)