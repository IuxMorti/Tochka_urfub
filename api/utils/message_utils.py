import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException

from config import EMAIL_ADDRESS, EMAIL_PASS, APP_HOST, APP_PORT


def send_verify_message(token, email):
    text = f"""<html>
      <body>
      <p>Здравствуйте. Вы прошли регистрацию на сайте brave-urfub.</p>
      <p>
        пройдите по ссылке: <a href='http://{APP_HOST}:{APP_PORT}/verificacion/{token}'>http://{APP_HOST}:{APP_PORT}g/verificacion/{token}</a>,
         чтобы подтверить вашу учетную запись.
      </p>
      <p> Если вы не регистрировались на сайте, то проигнорируйте данное сообщение. </p>
      </body>
    </html>"""
    send(text, email)


def send_reset_message(token, email):
    text = f"""<html>
      <body>
      <p>Здравствуйте. Вы поступил запрос на смену пароля на сайте brave-urfub.</p>
      <p>
        пройдите по ссылке: <a href='http://{APP_HOST}:{APP_PORT}/reset-password/{token}'>http://{APP_HOST}:{APP_PORT}/reset-password/{token}</a>
        если вы и вправду хотите поменять свой пароль.
      </p>
      <p> Если вы не делали запрос, то проигнорируйте данное сообщение. </p>
      </body>
    </html>"""

    send(text, email)


def send(text, email):
    server = smtplib.SMTP_SSL("smtp.yandex.ru", 465)
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS

    msg['To'] = email

    msg['Subject'] = "it's test"

    msg.attach(MIMEText(text, 'html'))
    try:
        server.login(msg['From'], EMAIL_PASS)
        server.sendmail(msg["From"], msg["To"], msg.as_string())
    except Exception as ex:
        raise HTTPException(400, ex.args)
