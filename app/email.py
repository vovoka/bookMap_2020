import os
from threading import Thread

from flask_mail import Message

from app import app, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_email_bi_is_expired(recipients: str, expired_bis: list):
    """
    Args:
     - recipients(str) - user's email
     - list of the user expired book_instances
    """
    domain = 'http://127.0.0.1:5000/'  # ! TODO replace with config vars
    subject = 'Some your books needs to be updated'
    sender = os.environ.get('MAIL_USERNAME')
    recipients = [recipients]
    text_body = """ Your next books are expired.
    Please, log in and update it's status \n\n"""
    for bi in expired_bis:
        text_body += f'{bi} \n'
    text_body += '\n BR, BookLib team'
    html_body = f'<h2>{subject}</h2>\n<p> Your next books are expired:</p>'
    for bi in expired_bis:
        html_body += f"<hr><b>{bi['title']}</b></br> by {bi['author']}\n"
    html_body += f'''</br>To update your books status
    <a href="{domain}">Login</a>
    and visit your profile page</br> BR, Booklib team.'''
    send_email(subject, sender, recipients, text_body, html_body)


def send_email_got_new_message(
        recipients: list,
        body: str,
        book_title: str) -> None:
    """
    Send an email with notification that the addressee got new message.
    Args:
        - sender(str)
        - recipients(list) - list with only email message recipient
        - body(str) - message body
        - book_title(str) - book_title
    """

    domain = 'http://127.0.0.1:5000/'
    subject = 'You got new private message'
    message_body = body
    sender = os.environ.get('MAIL_USERNAME')
    recipients = [recipients]
    text_body = f""" You got next message related to book "{book_title}".
    Please, log in and reply. \n\n
    {message_body} \n
    BR, BookLib team"""
    html_body = f'''<h2> {subject} </h2> You got next message related to book
    "{book_title}".</br>
     <p>{message_body}</p></br>
     Please, </br><a href="{domain}">login</a> to answer.</br>
     BR, BookLib team '''
    send_email(subject, sender, recipients, text_body, html_body)
