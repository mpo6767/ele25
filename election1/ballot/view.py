from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint)
from election1.ballot.form import (CandidateForm, OfficeForm,
                                   ClassgrpForm, Candidate_reportForm, DatesForm)
from election1.models import Classgrp, Office, Candidate, Dates
from election1.extensions import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

ballot = Blueprint('ballot', __name__)


@ballot.route('/office', methods=['POST', 'GET'])
def office():
    office_form = OfficeForm()
    if office_form.validate_on_submit():
        office_title = request.form['office_title']
        sortkey = request.form['sortkey']
        office_vote_for = request.form['office_vote_for']
        new_office = Office(office_title=office_title, sortkey=sortkey, office_vote_for=office_vote_for)

        try:
            db.session.add(new_office)
            db.session.commit()
            # flash('successfully updates record', category='success')
            office_form.office_title.data = ''
            office_form.sortkey.data = None
            offices = Office.query.order_by(Office.sortkey)
            return render_template('office.html', form=office_form, offices=offices)
        except Exception as e:
            db.session.rollback()
            flash('There was a problem inserting record ' + str(e), category='danger')
            office_form.office_title.data = ''
            office_form.sortkey.data = None
            offices = Office.query.order_by(Office.sortkey)
            return render_template('office.html', form=office_form, offices=offices)
    else:
        for err_msg in office_form.errors.values():
            flash(f'there is an error creating office: {err_msg}', category='danger')
            offices = Office.query.order_by(Office.sortkey)
            return render_template('office.html', form=office_form, offices=offices)

    office_form.office_title.data = ''
    office_form.sortkey.data = None
    # office_form.office_vote_for = 1
    offices = Office.query.order_by(Office.sortkey)
    return render_template('office.html', form=office_form, offices=offices)


@ballot.route('/deleteoffice/<int:xid>', methods=['POST', 'GET'])
def deleteoffice(xid):
    office_to_delete = Office.query.get_or_404(xid)
    form = CandidateForm()
    if request.method == 'POST':

        try:
            db.session.delete(office_to_delete)
            db.session.commit()
            flash('successfully deleted record', category='success')
            return redirect('/office')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('There was a problem deleting record' + str(e))
            return redirect('/office')
    else:

        candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
            Office).order_by(Classgrp.sortkey, Office.sortkey).where(Candidate.id_office == id)
        return render_template('office_candidate_delete.html', form=form, candidates=candidates,
                               office_to_delete=office_to_delete)


@ballot.route('/updateoffice/<int:xid>', methods=['GET', 'POST'])
def updateoffice(xid):
    office_form = OfficeForm()
    office_to_update = Office.query.get_or_404(xid)
    print(office_to_update.office_title)
    if request.method == "POST":
        office_to_update.office_title = request.form['office_title']
        office_to_update.sortkey = request.form['sortkey']
        try:
            db.session.commit()
            flash('successfully updates record', category='success')
            office_form.office_title.data = ''
            office_form.sortkey.data = ''
            offices = Office.query.order_by(Office.sortkey)
            return render_template('office.html', form=office_form, offices=offices)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('There was a problem updating record record' + str(e), category='danger')
            office_form.office_title.data = ''
            office_form.sortkey.data = ''
            offices = Office.query.order_by(Office.sortkey)
            return render_template('office.html', form=office_form, offices=offices)
    else:
        print("gere")
        return render_template('update_office.html', form=office_form,
                               office_to_update=office_to_update)


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
            classgrps = Classgrp.query.order_by(Classgrp.sortkey)
            return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)

    classgrp_form.name.data = ''
    classgrp_form.sortkey.data = None
    classgrps = Classgrp.query.order_by(Classgrp.sortkey)
    return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)


@ballot.route('/deleteclass/<int:xid>')
def deleteclass(xid):
    classgrp_to_delete = Classgrp.query.get_or_404(xid)

    try:
        db.session.delete(classgrp_to_delete)
        db.session.commit()
        # flash('successfully deleted record',category='success')
        return redirect('/classgrp')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('There was a problem deleting record' + str(e), category='danger')
        return redirect('/classgrp')


@ballot.route('/updateclass/<int:xid>', methods=['GET', 'POST'])
def updateclass(xid):
    classgrp_form = ClassgrpForm()
    classgrp_to_update = Classgrp.query.get_or_404(xid)
    print(classgrp_to_update.name)
    if request.method == "POST":
        classgrp_to_update.name = request.form['name']
        classgrp_to_update.sortkey = request.form['sortkey']
        try:
            db.session.commit()
            flash('successfully updates record', category='success')
            classgrp_form.name.data = ''
            classgrp_form.sortkey.data = ''
            classgrps = Classgrp.query.order_by(Classgrp.sortkey)
            return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('There was a problem updating record record ' + str(e), category='danger')
            classgrp_form.name.data = ''
            classgrp_form.sortkey.data = ''
            classgrps = Classgrp.query.order_by(Classgrp.sortkey)
            return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)
    else:
        print("gere")
        return render_template('update_classgrp.html', form=classgrp_form,
                               classgrp_to_update=classgrp_to_update)


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
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('problem adding candidate ' + str(e), category='danger')
            return redirect('/candidate')
    else:
        candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
            Office).order_by(Classgrp.sortkey, Office.sortkey)
        return render_template('candidate.html', form=form, candidates=candidates)


@ballot.route('/deletecandidate/<int:xid>')
def deletecandidate(xid):
    candidate_to_delete = Candidate.query.get_or_404(xid)

    try:
        db.session.delete(candidate_to_delete)
        db.session.commit()
        flash('successfully deleted record')
        return redirect('/candidate')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('There was a problem deleting record ' + str(e))
        return redirect('/candidate')


@ballot.route('/dates', methods=['GET', 'POST'])
def dates():
    form = DatesForm()
    print(DatesForm.errors)
    if request.method == 'POST':
        if form.validate_on_submit():
            # if request.method == 'POST':
            # these worked with mySQL but not SQLite
            # SQLite does not have a datetime column used Integer and epoch
            #
            # start_date_time = request.form.get('start_date_time')
            # end_date_time = request.form.get('end_date_time')
            # new_dates = Dates(start_date_time=start_date_time,end_date_time=end_date_time)
            # db.session.add(new_dates)
            # db.session.commit()

            #

            datetime_str = request.form.get('start_date_time').replace("T", " ")
            datetime_etr = request.form.get('end_date_time').replace("T", " ")

            datetime_object_start = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            datetime_object_end = datetime.strptime(datetime_etr, '%Y-%m-%d %H:%M')

            epoch_start_time = int(datetime_object_start.timestamp())
            epoch_end_time = int(datetime_object_end.timestamp())

            new_dates = Dates(start_date_time=epoch_start_time, end_date_time=epoch_end_time)
            db.session.add(new_dates)
            db.session.commit()

            return redirect(url_for('mains.homepage'))
    print('edates')
    edate_dict = {}
    edates = Dates.query.all()
    if edates is not None:
        for edate in edates:
            new_edate_dict = {
                "id": edate.iddates,
                "start": datetime.fromtimestamp(edate.start_date_time),
                "end": datetime.fromtimestamp(edate.end_date_time)
            }
            edate_dict.update(new_edate_dict)
    print(edate_dict)
    return render_template('dates.html', form=form, edate_dict=edate_dict)


@ballot.route('/deletedates/<int:xid>')
def deletedates(xid):
    date_to_delete = Dates.query.get_or_404(xid)

    try:
        db.session.delete(date_to_delete)
        db.session.commit()
        flash('successfully deleted record')
        return redirect('/dates')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('There was a problem deleting record ' + str(e))
        return redirect('/dates')
