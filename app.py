from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from database import load_jobs_from_db, load_job_from_db, add_application_to_db
from smtplib import SMTP_SSL as SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

app = Flask(__name__)
app.secret_key = '3f!x$k9a2@d8#pQm'

# MySQL connection (update with your actual credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error = "User already exists! Please login or use another email."
            return render_template('register.html', error=error)
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        session['user'] = email
        return redirect('/dashboard')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user'] = email
            return redirect('/dashboard')
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    user = session.get('user') 
    if 'user' not in session:
        return redirect('/login')
        
    return render_template('dashboard.html',user=user)
    

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

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
    Chuvek Career Team
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
