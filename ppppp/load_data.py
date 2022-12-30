import json
import os

from app.models import Company, CompanyCategory, ProductCategory
from app import db



class LoadData():

    def __init__(self, load_company: bool, load_category: bool=True):
        self.load_category = load_category
        self.load_company = load_company

    def __company_category_load(self, data):

        for cat in data:
            com_cat = CompanyCategory(
                title=cat['title'], 
                title_ru=cat['title_ru']
                )
            db.session.add(com_cat)
        db.session.commit()


    def __product_category_load(self, data):

        for cat in data:
            prod_cat = ProductCategory(
                title=cat['title'], 
                category_id=int(cat['category_id'])
                )
            db.session.add(prod_cat)
        db.session.commit()
        
    def __create_category(self):
        
        work_dir = os.getcwd()
        with open(work_dir+'/app/static/data/category_data.json') as f:
            data = json.load(f)

        self.__company_category_load(data['CompanyCategory'])
        self.__product_category_load(data['ProductCategory'])


    def create_data(self):
        print('sdgasdf sdgdsgdsg sdgsdg 35635763573573')
        if self.load_category:
            self.__create_category()



