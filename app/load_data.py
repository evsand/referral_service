import json
import os

from app.models import Company, CompanyCategory, ProductCategory
from app import db
from faker import Faker


class LoadData():

    def __init__(self, load_company: bool, load_category: bool = True):
        self.load_category = load_category
        self.load_company = load_company
        self.work_dir = os.getcwd()

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

    @staticmethod
    def __check_prod_category():
        count_prod = len(db.session.query(ProductCategory).all())
        if count_prod == 0:
            return True
        return False

    @staticmethod
    def __check_comp_category():
        count_comp = len(db.session.query(CompanyCategory).all())        
        if count_comp == 0:
            return True
        return False

    def __create_category(self):
        
        with open(self.work_dir+'/app/static/data/category_data.json') as f:
            data = json.load(f)

        if self.__check_prod_category():
            self.__product_category_load(data['ProductCategory'])
        if self.__check_comp_category():
            self.__company_category_load(data['CompanyCategory'])

    @staticmethod
    def __check_company():
        count_comp = len(db.session.query(Company).all())        
        if count_comp == 0:
            return True
        return False

    def __company_load(self):
        
        with open(self.work_dir+'/app/static/data/company_data.json', 'r') as f:
            company_data = json.load(f)

        for company_data_category in company_data.keys():
                    
            company_category_id = db.session.query(CompanyCategory)\
                .where(CompanyCategory.title == company_data_category).first()

            for i in company_data[company_data_category]:
                new_email = i['title'].replace(' ', '') + '@test.test'
                hashed_password = 'test'
                faker = Faker('ru_RU')

                new_company = Company(
                    title=i['title'],
                    email=new_email,
                    hashed_psw=hashed_password,
                    category_id=company_category_id.id,
                    description=i['description'],
                    logo=i['photo'],
                    phone_number=faker.phone_number(),
                    address=faker.address(),
                )

                db.session.add(new_company)
        db.session.commit()

    def __create_company(self):
        if self.__check_company():
            self.__company_load()

    def create_data(self):
        if self.load_category:
            self.__create_category()
        if self.load_company:
            self.__create_company()
