# To send notification email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sendemail(message):
    sender_email = "rtshibay@gmail.com"
    receiver_email = "sgao@bnl.gov;gao33.bnl@gmail.com;lke@bnl.gov"
    password = "mbqx qfca voue zwfr"
    subject = "Message from RTS"
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
