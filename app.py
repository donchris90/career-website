from flask import Flask, render_template, request
from database import load_jobs_from_db, load_job_from_db, add_application_to_db
from smtplib import SMTP_SSL as SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

app = Flask(__name__)

@app.route("/")
def home():
    jobs = load_jobs_from_db()
    return render_template("home.html", jobs=jobs, company_name='Christo')

@app.route("/job/<id>")
def show_job(id):
    job = load_job_from_db(id)
    if not job:
        return "Not Found", 404
    return render_template("jobpage.html", job=job)

@app.route("/job/<id>/apply", methods=['POST'])
def apply_to_job(id):
    application = request.form
    job = load_job_from_db(id)

    add_application_to_db(id, application)

    # Send notification email
    send_notification_email(application, job)

    return render_template("application_sumitted.html", application=application, job=job)

def send_notification_email(application, job):
    sender = os.environ.get('EMAIL_USER')          # e.g. 'your_email@gmail.com'
    password = os.environ.get('EMAIL_PASSWORD')         # Gmail App Password
    recipient = application['email']                # or HR email

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = f"Application Received for {job['title']}"

    body = f"""
    Dear {application['full_name']},

    Thank you for applying for the position of {job['title']}.
    We have received your application and will review it shortly.

    Best regards,  
    Christo Career Team
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        with SMTP('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, [recipient], msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print("Failed to send email:", e)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
