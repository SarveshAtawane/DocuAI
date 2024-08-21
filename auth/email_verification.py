# File: auth/email_verification.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import os
from jinja2 import Template

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def read_template(filename):
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(script_dir, 'templates', filename)
    with open(template_path, 'r', encoding='utf-8') as template_file:
        template_content = template_file.read()
    return Template(template_content)

def send_email_with_otp(receiver_email: str,username:str):
    # Email configuration
    sender_email = "sarveshtawane@gmail.com"
    sender_password = "dppp zakp mldu nzyq"
    receiver_email = receiver_email
    sender_name = "SAASyQiD"
    subject = "Your OTP for Verification"
    
    # Generate OTP
    otp = generate_otp()
    
    # Read HTML template
    template = read_template('emailtemplate.html')
    # Render the template with variables
    html_content = template.render(otp=otp, sender_name="Sarvesh",username = username)

    # Create the email message
    message = MIMEMultipart("alternative")
    message["From"] = f"{sender_name} <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add HTML content
    message.attach(MIMEText(html_content, "html"))

    try:
        # Create a secure SSL context
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(message)
        print(f"Email sent successfully with OTP: {otp}")
        return otp
    except Exception as e:
        print(f"An error occurred: {str(e)}")

