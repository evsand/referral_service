from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from sqlalchemy_utils import PhoneNumberType
import phonenumbers

from app.models import Users


class LoginForm(FlaskForm):
    email = StringField(
        "Email: "
        , validators=[Email("Некорректный email")]
    )
    password = PasswordField(
        "Пароль: ",
        validators=[
            DataRequired(),
            Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")]
    )
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    first_name = StringField(
        "Имя: ",
        validators=[Length(min=2, max=50, message="Имя должно быть от 2 до 50 символов")]
    )
    second_name = StringField(
        "Фамилия: ",
        validators=[Length(min=2, max=50, message="Фамилия должна быть от 2 до 50 символов")]
    )
    email = StringField(
        "Email: ",
        validators=[Email("Некорректный email")]
    )
    password = PasswordField(
        "Пароль: ",
        validators=[
            DataRequired(),
            Length(min=4, max=100, message="Пароль должен быть от 4 до 50 символов")
        ]
    )
    password2 = PasswordField(
        "Повторите пароль: ",
        validators=[
            DataRequired(),
            EqualTo('password', message="Пароли не совпадают")]
    )
    gender = RadioField(
        "Пол:",
        choices=[('Мужской'), ('Женский')]
    )
    phone_number = StringField(
        'Номер телефона',
        validators=[DataRequired()]
    )
    submit = SubmitField("Регистрация")

    def validate_phone(self, phone_number):
        try:
            p = phonenumbers.parse(phone_number.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Неверный номер телефона')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            flash('Этот емайл уже занят. Пожалуйста, введите другой', 'danger')
            raise ValidationError('That email is taken. Please choose a different one')


class RequestResetForm(FlaskForm):
    email = StringField('Емайл', validators=[DataRequired(), Email()])
    submit = SubmitField('Сбросить пароль')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is None:
            flash('Нет аккаунта с такой электронной почтой', 'danger')
            raise ValidationError('There is no account with that email. You must register first')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Сбросить пароль')
