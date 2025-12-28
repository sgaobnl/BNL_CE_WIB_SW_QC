import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
def send_email(sender_email, sender_password, receiver_email, subject, body):
   message = MIMEMultipart()
   message['From'] = sender_email
   message['To'] = receiver_email
   message['Subject'] = subject
   message.attach(MIMEText(body, 'plain'))
   try:
       server = smtplib.SMTP('smtp.gmail.com', 587)
       server.starttls()  # 启用TLS加密
       server.login(sender_email, sender_password)
       text = message.as_string()
       server.sendmail(sender_email, receiver_email, text)
       print("Please Check Email!")
   except Exception as e:
       print(f"Email send fail ... : {e}")

   finally:
       server.quit()

# 使用示例
# sender = "bnlr216@gmail.com"
# password = "vvef tosp minf wwhf"
# receiver = "lke@bnl.gov"
#
# send_email(sender, password, receiver,
#           "Test",
#           "New Email")