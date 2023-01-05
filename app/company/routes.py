import os

from flask import jsonify, url_for, make_response, render_template
from app.company import bp
from app.models import *


@bp.route('/')
def get_all_companies():

    companies = Company.query.all()
    base_workdir = os.getcwd()
    img_path = base_workdir + f'/app/static/users_img/'
    return render_template("company/company.html", companies=companies, img_path=img_path)


@bp.route('/<company_name>')
def test(company_name):

    company = Company.query.where(Company.title == company_name).first()
    if company:
        img_name = company.logo
        comp_category = company.category.title
        
        img_path = f'/static/users_img/{comp_category}/{img_name}'

        return render_template("company/detail.html", company=company, img_path=img_path)

    else:
        return jsonify({'Not': 'found'})
