from flask import render_template, request, Blueprint

mains = Blueprint('mains', __name__)

@mains.route('/')
@mains.route('/home')
@mains.route('/homepage')
def homepage():

    # return 'homepage.html'
    return render_template('homepage.html')
    # return "I like to eat potato"


@mains.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')
