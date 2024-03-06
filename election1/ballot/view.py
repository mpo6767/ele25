from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from election1.ballot.form import CandidateForm, OfficeForm, ClassgrpForm, Candidate_reportForm
from election1.models import Classgrp, Office, Candidate
from election1.extensions import db
import logging


ballot = Blueprint('ballot', __name__)

@ballot.route('/office', methods=['POST', 'GET'])
def office():
    office_form = OfficeForm()
    print("1")
    if office_form.validate_on_submit():
        print("2")
        office_title = request.form['office_title']
        sortkey = request.form['sortkey']
        new_office = Office(office_title=office_title, sortkey=sortkey)
        print("A")
        db.session.add(new_office)
        db.session.commit()
        # else:
        #     pass
    else:
        for err_msg in office_form.errors.values():
            flash(f'there is an error creating office: {err_msg}', category='danger')

    office_form.office_title.data = ''
    office_form.sortkey.data = ''
    offices = Office.query.order_by(Office.sortkey)
    return render_template('office.html', form=office_form, offices=offices)


@ballot.route('/deleteoffice/<int:id>',methods=['POST', 'GET'])
def deleteoffice(id):
    office_to_delete = Office.query.get_or_404(id)
    form = CandidateForm()
    if request.method == 'POST':

        try:
            db.session.delete(office_to_delete)
            db.session.commit()
            flash('successfully deleted record', category='success')
            return redirect('/office')
        except:
            db.session.rollback()
            flash('There was a problem deleting record')
            return redirect('/office')
    else:
        the_office = db.session.query(Office).where(Office.id_office == id)
        candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
            Office).order_by(Classgrp.sortkey, Office.sortkey).where(Candidate.id_office == id)
        return render_template('offiice_candidate_delete.html', form=form, candidates=candidates,
                               office_to_delete=office_to_delete)


@ballot.route('/classgrp', methods=['POST', 'GET'])
def classgrp():
    classgrp_form = ClassgrpForm()
    if classgrp_form.validate_on_submit():
        classgrp_name = request.form['name']
        sortkey = request.form['sortkey']
        new_classgrp = Classgrp(name=classgrp_name, sortkey=sortkey)
        db.session.add(new_classgrp)
        db.session.commit()
        flash('successfully added record', category='success')
    else:
        for err_msg in classgrp_form.errors.values():
            flash(f'there is an error creating a class or group: {err_msg}', category='danger')

    classgrp_form.name.data = ''
    classgrp_form.sortkey.data = ''
    classgrps = Classgrp.query.order_by(Classgrp.sortkey)
    return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)


@ballot.route('/deleteclass/<int:id>')
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


@ballot.route("/candidate_report", methods=['GET', 'POST'])
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


@ballot.route('/candidate', methods=['GET', 'POST'])
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
            return redirect(url_for('ballot.candidate'))
        except:
            db.session.rollback()
            flash('problem adding candidate', category='danger')
            return redirect('/candidate')
    else:
        candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
            Office).order_by(Classgrp.sortkey, Office.sortkey)
        return render_template('candidate.html', form=form, candidates=candidates)


@ballot.route('/deletecandidate/<int:id>')
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






