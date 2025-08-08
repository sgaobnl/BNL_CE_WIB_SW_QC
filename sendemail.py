# To send notification email
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google_sheets_shifter import google_sheets_shifter
from datetime import date

def sendemail(message, user_email="", subject = "Message from RTS", inform_tech = False, p_shifter=True, s_shifter=False):
    shifters = google_sheets_shifter()

    sender_email = "rtshibay@gmail.com"
    if inform_tech:
        email_list_fp = "./tech_email_list.csv"
        if os.path.isfile(email_list_fp):
            tech_emails = ""
            with open(email_list_fp , 'r') as fp:
                for cl in fp:
                    tmp = cl.split(",")
                    tech_emails = tech_emails + ";" + tmp[0]
        receiver_email = "sgao@bnl.gov;gao33.bnl@gmail.com;" + tech_emails + ";" + user_email
    else:
        receiver_email = "sgao@bnl.gov;gao33.bnl@gmail.com;" + user_email
        today = date.today()
        weekday_iso = today.isoweekday()
    if p_shifter:
        receiver_email = ";".join([receiver_email, shifters[weekday_iso][0]])
    if s_shifter:
        receiver_email = ";".join([receiver_email, shifters[weekday_iso][1]])
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

#sendemail(message="ehllo", user_email="", subject = "Message from RTS", inform_tech = False, p_shifter=True, s_shifter=True)
