import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configparser import ConfigParser

id_score_map = {'001':100, '002':0}

config = ConfigParser()
config.read('email.config')

imap_server = config['server']['imap']
user = config['server']['user']
password = config['server']['password']

mail = imaplib.IMAP4_SSL(imap_server)
mail.login(user, password)

mail.select("INBOX")

result, data = mail.uid('search', None, 'ALL')
inbox_item_list = data[0].split()

most_recent = inbox_item_list[-1]
result2, email_data = mail.uid('fetch', most_recent, '(BODY.PEEK[])')

raw_email = email_data[0][1].decode("utf-8")
email_message = email.message_from_string(raw_email)

subject = decode_header(email_message['Subject'])[0][0]
if isinstance(subject, bytes):
    subject = subject.decode()

if subject[:6] == '期末成绩查询':
    student_id = subject[-3:]
    if student_id in id_score_map:
        score = id_score_map[student_id]

        smtp_server = config['server']['smtp']

        server = smtplib.SMTP(smtp_server)
        server.starttls()

        server.login(user, password)

        msg = MIMEMultipart()
        msg['From'] = user
        msg['To'] = email_message['From']
        msg['Subject'] = "期末成绩"
        body = "Your score is " + str(score)
        msg.attach(MIMEText(body, 'plain'))

        text = msg.as_string()
        server.sendmail(user, email_message['From'], text)

        server.quit()