from sqlalchemy import create_engine,text
import os



db_connection_string = os.getenv('DB_CONNECTION_STRING')
if db_connection_string is None:
    raise RuntimeError("Environment variable DB_CONNECTION_STRING is not set.")

engine = create_engine(db_connection_string,connect_args={
                       "ssl": {
                          "ca": "isrgrootx1.pem",
                           
                       }}
                      )

def load_jobs_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from jobs"))
    jobs = []
    for row in result.all():
        jobs.append(row)
    return jobs
    
def load_job_from_db(id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM jobs WHERE id = :val"),
            {"val": id}
        )
        row = result.mappings().fetchone()
        return dict(row) if row else None

        
def add_application_to_db(job_id, application):
    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO applications (
                    job_id, full_name, email, linkedin_url, education, work_experience, resume_url
                )
                VALUES (
                    :job_id, :full_name, :email, :linkedin_url, :education, :work_experience, :resume_url
                )
            """)

            result = conn.execute(query, {
                'job_id': job_id,
                'full_name': application['full_name'],
                'email': application['email'],
                'linkedin_url': application['linkedin_url'],
                'education': application['education'],
                'work_experience': application['work_experience'],
                'resume_url': application.get('resume_url', '')
            })

            conn.commit()  # Explicitly commit the transaction
            print("Application added successfully.")
    except Exception as e:
        print(f"Error: {e}")
