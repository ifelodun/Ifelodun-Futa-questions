import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this_should_be_changed'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///students.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email@gmail.com'  # Replace with your email
    MAIL_PASSWORD = 'your_email_password'   # Use App Password if Gmail
