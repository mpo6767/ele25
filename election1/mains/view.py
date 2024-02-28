from flask import render_template, request, Blueprint

mains = Blueprint('mains', __name__)

@mains.route('/')
@mains.route('/home')
@mains.route('/homepage')
def homepage():  # put application's code here
    # try:
    #     db.session.query(Office).all()
    #     logger.info('connection is good')
    #     return '<h1>It works.</h1>'
    # except OperationalError as e:
    #     return '<h1>' + str(e) + '</h1>'


    # return 'homepage.html'
    return render_template('homepage.html')


@mains.route('/dashboard',methods=['GET', 'POST'])
def dashboard():
     return render_template('dashboard.html')
