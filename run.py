import os
from flask import Flask
from election1 import create_app

app: Flask = create_app()

if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    app.run(debug=True)