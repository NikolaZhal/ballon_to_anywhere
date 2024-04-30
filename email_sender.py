import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def send_email(email, subject, text):
    with open('config.json') as file:
        data = json.load(file)
    addr_from = data['FROM']
    password = data['PASSWORD']

    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = email
    msg['Subject'] = subject

    body = text
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP_SSL(data['E_HOST'], data['E_PORT'])
        server.login(addr_from, password)
        server.send_message(msg)
        server.quit()
        return (True, 1)
    except Exception as e:
        return (False, e)


if __name__ == '__main__':
    print(send_email('ryazan62nik@yandex.ru', 'Teme', 'TExt text, text, text text text'))
