from flask import Flask, render_template
from database import *


app = Flask(__name__)


@app.route("/")
def home():
  jobs = load_jobs_from_db()
  return  render_template("home.html", jobs=jobs,company_name='Christo')

@app.route("/job/<id>")
def show_job(id):
  job = load_job_from_db(id)
  return render_template("jobpage.html", job=job)
  
 

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)