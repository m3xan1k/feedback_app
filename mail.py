import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_mail(user, password, title, text):

    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = user
    message["To"] = user

    message.attach(MIMEText(text, 'plain'))

    try:  
        server = smtplib.SMTP_SSL('smtp.yandex.com', 465)
        server.ehlo()
        server.login(user, password)
        server.sendmail(user, user, message.as_string())
        server.close()

        print('Email sent')
    except Exception as e: 
        print ('Something went wrong...')
        print(e)

if __name__ == '__main__':
    send_mail('Привет', 'Как дела?')
