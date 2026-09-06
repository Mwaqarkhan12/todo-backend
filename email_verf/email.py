from email.message import EmailMessage
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import os
from dotenv import load_dotenv
import smtplib

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Environment(loader=FileSystemLoader(BASE_DIR / "templates"))

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM")
# print("SMTP_HOST:", SMTP_HOST)
# print("SMTP_PORT:", SMTP_PORT)
# print("SMTP_USERNAME:", SMTP_USERNAME)
# print("SMTP_from email:", SMTP_FROM_EMAIL)

def send_email_verification(receiver_email:str, name:str, otp:str):
    # verf_url = f"http://localhost:8000/auth/verify-email"f"?token={otp}"

    template = templates.get_template("verify_email.html")
    html_content = template.render(name=name, otp=otp)

    mesage = EmailMessage()

    mesage["From"] = SMTP_FROM_EMAIL
    mesage["To"] = receiver_email
    mesage["Subject"] = "Verify Your Email"

    mesage.set_content(f"""Hello, Thank you for registering. Please verify your email by clicking the link below: {otp} If you did not create this account, you can ignore this email.
Thanks""")
    
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME,SMTP_PASSWORD)
        server.send_message(mesage)



# def send_email_verification(receiver_email: str, name: str, otp: str):
#     template = templates.get_template("verify_email.html")
#     html_content = template.render(name=name, otp=otp)

#     message = EmailMessage()

#     message["From"] = SMTP_FROM_EMAIL
#     message["To"] = receiver_email
#     message["Subject"] = "Verify Your Email"

#     message.set_content(
#         f"""Hello {name},

# Thank you for registering.

# Your verification OTP is: {otp}

# If you did not create this account, you can ignore this email.

# Thanks"""
#     )

#     message.add_alternative(html_content, subtype="html")

#     with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
#         server.starttls()
#         server.login(SMTP_USERNAME, SMTP_PASSWORD)
#         server.send_message(message)

