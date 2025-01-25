from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


SMTP_SERVER = 'smtp.gmail.com'  # Use your SMTP server
SMTP_PORT = 587                 # Typically 587 for TLS
SMTP_USERNAME = 'mohank.tangirala@gmail.com'
SMTP_PASSWORD = os.getenv('google_app_password') 

# Initialize the app
app = Flask(__name__)

# Enable CORS for frontend requests
CORS(app)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///form_data.db'  # You can use MySQL/PostgreSQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database model for form data
class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<FormData {self.name}>"

# Initialize the database
with app.app_context():
    db.create_all()

# Email validation function
def is_valid_email(email):
    # Check if email contains '@' and ends with '.com'
    if '@' in email and email.endswith('.com'):
        return True
    return False

# Endpoint to handle form submission
@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Get form data from frontend
    data = request.json
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    # Validate email
    if not is_valid_email(email):
        return jsonify({"status": "error", "message": "Enter a valid email with '@' and '.com'"}), 400
    
    message_body = f"Here is your new user {name}\n\nEmail->{email}\n\nThe Message\n{message}"
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = 'mohankrishna.portfolio@gmail.com'
    msg['Subject'] = 'New user'
    msg.attach(MIMEText(message_body, 'plain'))

    # Send email using SMTP
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, 'mohankrishna.portfolio@gmail.com', msg.as_string())

     # Save the data to the database
    new_entry = FormData(name=name, email=email, message=message)
    db.session.add(new_entry)
    db.session.commit()
    print("Mail sent successfully.")

    # Return a success response after saving to the database
    return jsonify({"status": "success", "message": "Form and email submitted successfully!"}), 200




   
if __name__ == '__main__':
    app.run(debug=True)
