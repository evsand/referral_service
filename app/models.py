from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50),  nullable=True)
    second_name = db.Column(db.String(50),  nullable=True)
    email = db.Column(db.String(50), unique=True)
    hashed_psw = db.Column(db.String(500))
    gender = db.Column(db.String(500), nullable=True)
    city = db.Column(db.String(500), nullable=True)
    phone_number = db.Column(db.String(500), unique=True, nullable=True)
    photo = db.Column(db.String(500), default='') # добавить дефолтное фото
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'User {self.id}'

    def set_password(self, password):
        self.hashed_psw = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_psw, password)


class CompanyCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)


class Company(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=True)
    hashed_psw = db.Column(db.String(500), nullable=True)
    phone_number = db.Column(db.String(500), unique=True, nullable=True)
    main_address = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    logo = db.Column(db.String, default='')  # добавить дефолтное фото
    category_id = db.Column(db.Integer, db.ForeignKey(CompanyCategory.id))

    def __repr__(self):
        return f'<Company  {self.title}>'


class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    discount = db.Column(db.Integer, nullable=True)
    award = db.Column(db.Integer, nullable=True)
    amount = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=False)


class ProductCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Integer, nullable=True)
    photo = db.Column(db.String, default='') #добавить дефолтное фото
    company_id = db.Column(db.Integer, db.ForeignKey(CompanyCategory.id))
    coupon_id = db.Column(db.Integer, db.ForeignKey(Coupon.id))
    product_category_id = db.Column(db.Integer, db.ForeignKey(Coupon.id))


class CreatedCoupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey(Coupon.id))
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    activations_count = db.Column(db.Integer, default=0)
    token = db.Column(db.String(500), nullable=True)
