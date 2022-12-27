from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import Users


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    password = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    first_name = StringField("Имя: ", validators=[Length(min=2, max=50, message="Имя должно быть от 2 до 50 символов")])
    second_name = StringField("Фамилия: ", validators=[Length(min=2, max=50, message="Фамилия должна быть от 2 до 50 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    password = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль должен быть от 4 до 50 символов")])
    password2 = PasswordField("Повторите пароля: ", validators=[DataRequired(), EqualTo('password', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Request Password Reset')
