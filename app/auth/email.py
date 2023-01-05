from flask import current_app, url_for
from flask_mail import Message
from app import mail
from threading import Thread


def send_confirm_email(user):
    token = user.generate_confirmation_token()
    msg = Message('Подтверждение регистрации',
                  sender='Referral Service',
                  recipients=[user.email])
    msg.body = f"""
    Чтобы подтвердить Ваш аккаунт, перейдите по этой ссылке:
    {url_for('auth.confirm_email', token=token, _external=True)}

    Если вы не делали данный запрос, просто проигнорируйте это письмо!
    Никаких изменений произведено не будет!

    Отвечать на данное письмо не нужно так как оно сгенерировано автоматически.
    """
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    msg = Message('Запрос на смену пароля',
                  sender='referralservice.helper@gmail.com',
                  recipients=[user.email])
    msg.body = f"""
    Чтобы сбросить ваш пароль, перейдите по этой ссылке:
    {url_for('auth.reset_password', token=token, _external=True)}

    Если вы не делали данный запрос, просто проигнорируйте это письмо!
    Никаких изменений произведено не будет!

    Отвечать на данное письмо не нужно так как оно сгенерировано автоматически.
    """
    mail.send(msg)


'''
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email,
            args=(current_app._get_current_object(), msg)).start()
'''