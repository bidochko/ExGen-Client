# import necessary packages

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def sendMessage(to, subject, message):
    # secret.txt is formatted as:
    # username \n
    # password \n
    with open('secret.txt') as f:
        lines = f.readlines()

    password = lines[1].split("\r\n")[0]

    # create message object instance
    msg = MIMEMultipart()

    # setup the parameters of the message
    msg['From'] = lines[0].split("\r\n")[0]
    msg['To'] = to
    msg['Subject'] = subject

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    #create server
    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()
