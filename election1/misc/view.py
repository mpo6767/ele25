from flask import url_for, flash, Blueprint, redirect, request, render_template, send_file
from pathlib import Path
import xlsxwriter
# from flask import Blueprint, redirect, request, render_template
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from election1.models import Tokenlist, Classgrp, Tokenlistselectors
from election1.utils import get_token
from election1.misc.form import BuildTokensForm
from election1.extensions import db
import qrcode
from io import BytesIO



misc = Blueprint('misc', __name__)
'''
this is code to make the token list in an excel file

the excel file is created in the instance folder and is a url to the cast route with the token as a parameter
'''
@misc.route('/setup_tokens', methods=['POST', 'GET'])
def setup_tokens():
    # print("setup_tokens")
    # Tokenlist.query.delete()
    # db.session.commit()

    form = BuildTokensForm()


    # if request.method == 'POST' and form.validate():
    if request.method == 'GET':
        print("setup_tokens")
        # Tokenlist.query.delete()
        # db.session.commit()

        inspector = inspect(db.engine)

        if not inspector.has_table('tokenlistselectors'):
            Tokenlistselectors.__table__.create(db.engine)
        # else:
        #     Tokenlistselectors.query.delete()
        #     db.session.commit()

        form.primary_grp.choices = Classgrp.classgrp_query()
        tokenlistselectors = Tokenlistselectors.query.all()

        return render_template("token_builder.html", form=form, tokenlistselectors=tokenlistselectors)
    else:
        print("setup_tokens post")
        if request.form.get('primary_grp') == 'Please select':
            flash('Primary group must be selected', category='danger')
            return redirect(url_for('misc.setup_tokens'))
        else:
            primary_grp = request.form.get('primary_grp')

        if request.form.get('secondary_grp') == 'Please select':
            secondary_grp = None
        else:
            secondary_grp = request.form.get('secondary_grp')

        if request.form.get('tertiary_grp') == 'Please select':
            tertiary_grp = None
        else:
            tertiary_grp = request.form.get('tertiary_grp')

        if request.form.get('quarternary_grp') == 'Please select':
            quarternary_grp = None
        else:
            quarternary_grp = request.form.get('quarternary_grp')


        if primary_grp != 'Please select':
            print("primary_grp")
            new_selector = Tokenlistselectors(
                primary_grp=primary_grp,
                secondary_grp=secondary_grp,
                tertiary_grp=tertiary_grp,
                quarternary_grp=quarternary_grp
            )
            try:
                db.session.add(new_selector)
                db.session.commit()
                flash('Tokenlistselector item added successfully', category='success')
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Error adding Tokenlistselector item: {str(e)}', category='danger')
        else:
            flash('Primary group must be selected', category='danger')

        return redirect(url_for('misc.setup_tokens'))


@misc.route('/delete_tokenlistselector/<int:xid>', methods=['GET', 'POST'])
def delete_tokenlistselector(xid):
    tokenlistselector = Tokenlistselectors.query.get_or_404(xid)

    try:
        db.session.delete(tokenlistselector)
        db.session.commit()
        flash('Tokenlistselector item deleted successfully', category='success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting Tokenlistselector item: {str(e)}', category='danger')

    return redirect(url_for('misc.setup_tokens'))

@misc.route('/build_tokens', methods=['GET', 'POST'])
def build_tokens():
    print("build_tokens")

    Tokenlist.query.delete()
    db.session.commit()

    # if there is a file voterTokens
    p = Path(r"instance/voterTokens.xlsx")
    p.unlink(missing_ok=True)

    workbook = xlsxwriter.Workbook(r'instance\voterTokens.xlsx')
    worksheet = workbook.add_worksheet()

    # Get the selected groups from the database

    tokenlistselectors = Tokenlistselectors.get_all_tokenlistselectors_as_dict()

    # selector_list is the list of the selected groups meant if there is more than 1
    # this list is used to create the excel file and is used asa roundrobin to select the group

    selector_list = []


    for selector in tokenlistselectors:
        selector_values = [
            selector['primary_grp'],
            selector['secondary_grp'],
            selector['tertiary_grp'],
            selector['quarternary_grp']
        ]
        # Filter out None values and join the remaining values with $
        selector_string = '$'.join(filter(None, selector_values))
        selector_list.append(selector_string)
        print("selector string " + selector_string)

    print(tokenlistselectors)

    selector_count = len(tokenlistselectors)
    print(selector_count)


    # Create a new Excel file

    p = Path(r"instance/voterTokens2.xlsx")
    p.unlink(missing_ok=True)

    workbook = xlsxwriter.Workbook(r'instance\voterTokens.xlsx')
    worksheet = workbook.add_worksheet()

    row = 0
    col = 0

    # Set the width of the first column to 120 characters
    worksheet.set_column(col, col, 120)

    while row < 101:
        token = get_token()
        eclass = row % selector_count
        print('eclass')
        print(eclass)
        print('tokenlistselector:', selector_list[eclass])

        row +=1

        try:
            new_tokenlist = Tokenlist(grp_list=selector_list[eclass],
                                      token=token,
                                      vote_submitted_date_time=None)
            db.session.add(new_tokenlist)
            db.session.commit()
            print('write ' + str(row))
        except SQLAlchemyError as e:
            db.session.rollback()
            print("except " + str(e))
            return redirect("/homepage")

        worksheet.write(row, col, 'http://127.0.0.1:5000/cast/' + selector_list[eclass] + '/' + token)
    workbook.close()
    return redirect('/homepage')

@misc.route('/single_token/<int:xid>', methods=['GET', 'POST'])
def single_token(xid):
    print("single_tokens")

    token = get_token()


    qrtoken = Tokenlistselectors.get_tokenlistselector_by_id_as_dict(xid)

    selector_values = [
        qrtoken['primary_grp'],
        qrtoken['secondary_grp'],
        qrtoken['tertiary_grp'],
        qrtoken['quarternary_grp']
    ]



    # Filter out None values and join the remaining values with $
    selector_string = '$'.join(filter(None, selector_values))
    print("selector string " + selector_string)

    try:
        new_tokenlist = Tokenlist(grp_list=selector_string,
                                  token=token,
                                  vote_submitted_date_time=None)
        db.session.add(new_tokenlist)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print("except " + str(e))
        return redirect("/homepage")

    qr_data = 'http://192.168.1.126:5000/cast/' + selector_string + '/' + token

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    print(qr_data)
    return send_file(img_io, mimetype='image/png')




