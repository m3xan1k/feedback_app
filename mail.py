import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(title, text):
    mail_user = 'dev.serzh@gmail.com'  
    mail_password = 'Fr331nt3rn3t666'

    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = mail_user
    message["To"] = mail_user

    message.attach(MIMEText(text, 'plain'))

    try:  
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(mail_user, mail_password)
        server.sendmail(mail_user, mail_user, message.as_string())
        server.close()

        print('Email sent')
    except Exception as e: 
        print ('Something went wrong...')
        print(e)

if __name__ == '__main__':
    send_mail('Привет', 'Как дела?')