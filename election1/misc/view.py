from pathlib import Path

import xlsxwriter
from flask import Blueprint, redirect
from sqlalchemy.exc import SQLAlchemyError
from election1.models import Tokenlist, Classgrp
from election1.utils import get_token

from election1.extensions import db


misc = Blueprint('misc', __name__)
'''
this is code to make the token list in an excel file

the excel file is created in the instance folder and is a url to the cast route with the token as a parameter
'''
@misc.route('/setup_tokens', methods=['POST', 'GET'])
def setup_tokens():
    Tokenlist.query.delete()
    db.session.commit()

    classgrp_list = Classgrp.classgrp_query()
    if not classgrp_list:
        print('No classgrp_list')
        return redirect('/homepage')
    else:
        print('classgrp_list')
        print(classgrp_list)

    classgrp_count = len(classgrp_list)
    print('classgrp_count')
    print(classgrp_count)

    # return redirect('/homepage')

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
        eclass = row % classgrp_count
        print('eclass')
        print(eclass)

        class_tuple = classgrp_list[eclass]
        grp_list = class_tuple[1]
        print('grp_list')
        print(grp_list)
        # if eclass == 1:
        #     grp_list = 'Freshmen'
        # if eclass == 2:
        #     grp_list = 'Sophomore$All'
        # if eclass == 3:
        #     grp_list = 'Junior'
        # if eclass == 0:
        #     grp_list = 'Senior'

        try:
            new_tokenlist = Tokenlist(grp_list=grp_list,
                                      token=token,
                                      vote_submitted_date_time=None)
            db.session.add(new_tokenlist)
            db.session.commit()
            print('write ' + str(row))
        except SQLAlchemyError as e:
            db.session.rollback()
            print("except " + str(e))
            return redirect("/homepage")

        print(row)
        worksheet.write(row, col, 'http://127.0.0.1:5000/cast/' + grp_list.lstrip() + '/' + token)
        #
        # if eclass == 1:
        #     worksheet.write(row, col, 'http://127.0.0.1:5000/cast/Freshmen/' + token)
        # elif eclass == 2:
        #     worksheet.write(row, col, 'http://127.0.0.1:5000/cast/Sophomore$All/' + token)
        # elif eclass == 3:
        #     worksheet.write(row, col, 'http://127.0.0.1:5000/cast/Junior/' + token)
        # elif eclass == 0:
        #     worksheet.write(row, col, 'http://127.0.0.1:5000/cast/Senior/' + token)

        row += 1

    workbook.close()
    return redirect('/homepage')
