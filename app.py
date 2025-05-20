from flask import Flask, render_template
from database import  load_jobs_from_db


app = Flask(__name__)


@app.route("/")
def home():
  jobs = load_jobs_from_db()
  return  render_template("home.html", jobs=jobs,company_name='Christo')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)