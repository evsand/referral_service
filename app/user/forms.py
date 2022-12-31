from flask_wtf import FlaskForm
from flask import flash
from flask_wtf.file import FileAllowed
from flask_login import current_user
from wtforms import StringField, SubmitField, FileField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
import phonenumbers

from app.models import Users


class UpdateAccountForm(FlaskForm):
    first_name = StringField(
        "Имя: ",
        validators=[Length(min=2, max=50,message="Имя должно быть от 2 до 50 символов")]
    )
    second_name = StringField(
        "Фамилия: ",
        validators=[Length(min=2, max=50, message="Фамилия должна быть от 2 до 50 символов")]
    )
    email = StringField('Емайл', validators=[DataRequired(), Email()])
    gender = RadioField("Пол:", choices=[('Мужской'), ('Женский')])
    phone_number = StringField('Номер телефона', validators=[DataRequired()])
    #picture = FileField('Изображение (png, jpj)', validators=[FileAllowed(['jpg', 'png']), ])
    submit = SubmitField('Обновить')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                flash('Этот емайл уже занят. Пожалуйста, введите другой', 'danger')
                raise ValidationError('That email is taken. Please choose a different one')

    def validate_phone(self, phone_number):
        try:
            p = phonenumbers.parse(phone_number.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
            if phone_number.data != current_user.phone:
                user = Users.query.filter_by(phone_number=phone_number.data).first()
                if user:
                    flash(
                        'Этот номер уже зарегистрирован. Пожалуйста, введите другой',
                        'danger'
                    )
                    raise ValidationError(
                        'That phone number is taken. Please choose a different one'
                    )
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Неверный номер телефона')