from election1 import app, db, login_manager
from flask import render_template, request, redirect, flash, url_for
from election1.models import Classgrp, Office, Candidate, Users
from election1.view import CandidateForm, OfficeForm, ClassgrpForm, Candidate_reportForm, UserForm, LoginForm
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required
import logging
# import os
# from datetime import date, datetime, timedelta


logger=logging.getLogger('simpleExample')





@app.route('/')
def homepage():  # put application's code here
    # try:
    #     db.session.query(Office).all()
    #     logger.info('connection is good')
    #     return '<h1>It works.</h1>'
    # except OperationalError as e:
    #     return '<h1>' + str(e) + '</h1>'


    # return 'homepage.html'
    return render_template('homepage.html')

@app.route('/office', methods=['POST', 'GET'])
def office():
    office_form = OfficeForm()
    if office_form.validate_on_submit():
        office_title = request.form['office_title']
        sortkey = request.form['sortkey']
        new_office = Office(office_title=office_title, sortkey=sortkey)
        db.session.add(new_office)
        db.session.commit()
        # return redirect('/office')
        # except:
        #     flash( "Error adding office" )
        #     return redirect('/office')
    # else:
    if office_form != {}:
        db.session.rollback()
        for err_msg in office_form.errors.values():
            flash(f'there is an error creating office: {err_msg}', category='danger')

    offices = Office.query.order_by(Office.sortkey)
    return render_template('office.html', form=office_form, offices=offices)


@app.route('/deleteoffice/<int:id>')
def deleteoffice(id):
    office_to_delete = Office.query.get_or_404(id)

    try:
        db.session.delete(office_to_delete)
        db.session.commit()
        flash('successfully deleted record', category='success')
        return redirect('/office')
    except:
        db.session.rollback()
        flash('There was a problem deleting record')
        return redirect('/office')


@app.route('/classgrp', methods=['POST', 'GET'])
def classgrp():
    classgrp_form = ClassgrpForm()
    if classgrp_form.validate_on_submit():
        classgrp_name = request.form['name']
        sortkey = request.form['sortkey']
        new_classgrp = Classgrp(name=classgrp_name, sortkey=sortkey)
        db.session.add(new_classgrp)
        db.session.commit()
        flash('successfully added record', category='success')
        return redirect(url_for('classgrp'))
    #         return redirect('/classgrp')
    #     except:
    #         flash("Error adding class or group", category='danger')
    #         return redirect('/classgrp')
    # else:
    if classgrp_form != {}:
        for err_msg in classgrp_form.errors.values():
            flash(f'there is an error creating a class or group: {err_msg}', category='danger')

    classgrps = Classgrp.query.order_by(Classgrp.sortkey)
    return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)


@app.route('/deleteclass/<int:id>')
def deleteclass(id):
    classgrp_to_delete = Classgrp.query.get_or_404(id)

    try:
        db.session.delete(classgrp_to_delete)
        db.session.commit()
        # flash('successfully deleted record',category='success')
        return redirect('/classgrp')
    except:
        db.session.rollback()
        flash('There was a problem deleting record', category='danger')
        return redirect('/classgrp')


@app.route("/candidate_report", methods=['GET', 'POST'])
def candidate_report():
    form = Candidate_reportForm()
    list_of_offices = db.session.query(Office).all()
    if request.method == 'POST':
        choices_classgrp = request.form['choices_classgrp']
        choices_office = request.form['choices_office']

        # the first if determines if the choice_office is an int 0
        # I built the candidate_report.html to add a choice of 'All Offices' which is not in the BD
        # I pass list_of_offices to the html and build the select offices manually fo this html
        if int(choices_office) == 0:
            candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
                Office).filter(Classgrp.id_classgrp == choices_classgrp)
            return render_template("candidate_report.html",
                                   form=form, candidates=candidates, list_of_offices=list_of_offices)
        else:
            candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
                Office).filter(Classgrp.id_classgrp == choices_classgrp, Office.id_office == choices_office)
            return render_template("candidate_report.html",
                                   form=form, candidates=candidates, list_of_offices=list_of_offices)

    else:
        return render_template("candidate_report.html", form=form, list_of_offices=list_of_offices)


@app.route('/candidate', methods=['GET', 'POST'])
def candidate():
    form = CandidateForm()
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        choices_classgrp = request.form['choices_classgrp']
        choices_office = request.form['choices_office']
        new_candidate = Candidate(firstname=firstname,
                                  lastname=lastname,
                                  id_classgrp=choices_classgrp,
                                  id_office=choices_office)

        try:
            db.session.add(new_candidate)
            db.session.commit()
            # flash('candidate added successfully',category='success')
            return redirect(url_for('candidate'))
        except:
            db.session.rollback()
            flash('problem adding candidate', category='danger')
            return redirect('/candidate')
    else:
        candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
            Office).order_by(Classgrp.sortkey, Office.sortkey)
        return render_template('candidate.html', form=form, candidates=candidates)


@app.route('/deletecandidate/<int:id>')
def deletecandidate(id):
    candidate_to_delete = Candidate.query.get_or_404(id)

    try:
        db.session.delete(candidate_to_delete)
        db.session.commit()
        flash('successfully deleted record')
        return redirect('/candidate')
    except:
        db.session.rollback()
        flash('There was a problem deleting record')
        return redirect('/candidate')

@app.route('/user_admin',methods=['GET', 'POST'])
def user_admin():
    form = UserForm()
    if request.method == 'POST':
        print("1")
        user_firstname = request.form['user_firstname']
        user_lastname = request.form['user_lastname']
        user_so_name = request.form['user_so_name']
        user_pass = request.form['user_pass']
        user_role = request.form['user_role']
        user_email = request.form['user_email']
        new_user = Users(user_firstname =user_firstname,
                        user_lastname = user_lastname,
                        user_so_name = user_so_name,
                        user_pass = user_pass,
                        user_role = user_role,
                        user_email = user_email)
        try:
            print("2")
            db.session.add(new_user)
            db.session.commit()
            flash('candidate added successfully',category='success')
            return redirect(url_for('user_admin'))
        except IntegrityError as e:
            print("3")
            db.session.rollback()
            logging.error("Duplicate entry user name: %s", e)
            flash('problem adding candidate duplicate username', category='danger')
            return redirect(url_for('user_admin'))
    print("4")
    return render_template('user.html', form=form)


@app.route('/login',methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)


@app.route('/dashboard',methods=['GET', 'POST'])
def dashboard():
     return render_template('dashboard.html')