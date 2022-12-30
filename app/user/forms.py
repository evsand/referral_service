from flask_wtf import FlaskForm
from flask import flash
from flask_wtf.file import FileAllowed
from flask_login import current_user
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import Users


class UpdateAccountForm(FlaskForm):
    first_name = StringField("Имя: ", validators=[Length(min=2, max=50,
                    message="Имя должно быть от 2 до 50 символов")])
    second_name = StringField("Фамилия: ",
        validators=[Length(min=2, max=50, message="Фамилия должна быть от 2 до 50 символов")])
    email = StringField('Емайл', validators=[DataRequired(), Email()])
    #picture = FileField('Изображение (png, jpj)', validators=[FileAllowed(['jpg', 'png']), ])
    submit = SubmitField('Обновить')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                flash('Этот емайл уже занят. Пожалуйста, введите другой', 'danger')
                raise ValidationError('That email is taken. Please choose a different one')