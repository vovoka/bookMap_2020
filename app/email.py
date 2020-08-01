from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail
import smtplib
import os


def send_email(recipients, subject, body):
    """
    # TODO made email sending in threads! (def send_async_email(app, msg)...)
    """

    sender = os.environ.get('MAIL_ADMIN')
    pwd = os.environ.get('MAIL_PASSWORD')
    recipients = recipients if isinstance(recipients, list) else [recipients]
    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (sender, ", ".join(recipients), subject, body)

    try:
        server = smtplib.SMTP(
            os.environ.get('MAIL_SERVER'),
            os.environ.get('MAIL_PORT'),
        )
        server.ehlo()
        server.starttls()
        server.login(sender, pwd)
        server.sendmail(sender, recipients, message)
        server.close()
        app.logger.info(f'Successfully sent the mail to {recipients}')
    except:
        app.logger.info(f'Failed to send mail to {recipients}')


def send_bi_is_expired_email(recipients:str, expired_bis:list):
    body = """ Your next books are expired. Please, log in and update it's status \n\n"""
    for bi in expired_bis:
        body += f'{bi} \n'
    body += '\n BR, BookLib team'

    send_email(
        recipients = recipients,
        subject = '[BookLib] Your Book Instance is expired',
        body=body,
    )
