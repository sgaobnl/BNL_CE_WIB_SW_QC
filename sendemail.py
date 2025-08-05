# To send notification email
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sendemail(message, user_email="", subject = "Message from RTS", inform_tech = False):

    sender_email = "rtshibay@gmail.com"
    if inform_tech:
        email_list_fp = "./tech_email_list.csv"
        if os.path.isfile(email_list_fp):
            tech_emails = ""
            with open(csvfp, 'r') as fp:
                for cl in fp:
                    tmp = cl.split(",")
                    tech_emails = tech_emails + ";" + tmp
        receiver_email = "sgao@bnl.gov;" + tech_emails + ";" + user_email
    else:
        receiver_email = "sgao@bnl.gov;" + user_email
    password = "mbqx qfca voue zwfr"
    
    body = message
    msg = MIMEMultipart()

    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    # Attach the body text to the email
    msg.attach(MIMEText(body, 'plain'))
    
    try: 
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()  # Start TLS encryption
            server.ehlo()
            server.login(sender_email, password)  # Login to the server
            server.send_message(msg)  # Send the email
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
