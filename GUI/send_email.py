import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# Default CC recipient for all test emails
DEFAULT_CC = "lke@bnl.gov"

def send_email(sender_email, sender_password, receiver_email, subject, body, cc_email=None):
   message = MIMEMultipart()
   message['From'] = sender_email
   message['To'] = receiver_email
   message['Subject'] = subject

   # Build CC list - always include DEFAULT_CC for test emails
   cc_list = []
   if cc_email:
       cc_list.append(cc_email)
   # Add default CC if receiver is different from DEFAULT_CC
   if receiver_email.lower() != DEFAULT_CC.lower() and DEFAULT_CC.lower() not in [c.lower() for c in cc_list]:
       cc_list.append(DEFAULT_CC)

   if cc_list:
       message['Cc'] = ', '.join(cc_list)

   message.attach(MIMEText(body, 'plain'))

   # Build recipient list for sendmail (includes To and Cc)
   all_recipients = [receiver_email] + cc_list

   try:
       server = smtplib.SMTP('smtp.gmail.com', 587)
       server.starttls()
       server.login(sender_email, sender_password)
       text = message.as_string()
       server.sendmail(sender_email, all_recipients, text)
       print("Please Check Email!")
   except Exception as e:
       print(f"Email send fail ... : {e}")

   finally:
       server.quit()

def send_email_with_attachment(sender_email, sender_password, receiver_email, subject, body, attachment_path=None, cc_email=None):
    """
    Send email with optional text file attachment

    Args:
        sender_email: Sender email address
        sender_password: Sender email password/app password
        receiver_email: Receiver email address
        subject: Email subject
        body: Email body text
        attachment_path: Optional path to text file to attach
        cc_email: Optional additional CC recipient
    """
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Build CC list - always include DEFAULT_CC for test emails
    cc_list = []
    if cc_email:
        cc_list.append(cc_email)
    # Add default CC if receiver is different from DEFAULT_CC
    if receiver_email.lower() != DEFAULT_CC.lower() and DEFAULT_CC.lower() not in [c.lower() for c in cc_list]:
        cc_list.append(DEFAULT_CC)

    if cc_list:
        message['Cc'] = ', '.join(cc_list)

    message.attach(MIMEText(body, 'plain'))

    # Attach file if provided
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)

                # Get filename from path
                filename = os.path.basename(attachment_path)
                part.add_header('Content-Disposition', f'attachment; filename= {filename}')
                message.attach(part)
                print(f"Attached file: {filename}")
        except Exception as e:
            print(f"Failed to attach file {attachment_path}: {e}")

    # Build recipient list for sendmail (includes To and Cc)
    all_recipients = [receiver_email] + cc_list

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, all_recipients, text)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Email send fail: {e}")
    finally:
        try:
            server.quit()
        except:
            pass

# 使用示例
# sender = "bnlr216@gmail.com"
# password = "vvef tosp minf wwhf"
# receiver = "lke@bnl.gov"
#
# send_email(sender, password, receiver,
#           "Test",
#           "New Email")