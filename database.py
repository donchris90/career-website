# database.py
from sqlalchemy import create_engine, text
import os

# Replace with your actual connection string
db_connection_string = os.environ['DB_CONNECTION_STRING']
engine = create_engine(db_connection_string, connect_args={
"ssl": {
    "ca": "isrgrootx1.pem",
}}
)
def load_job_from_db(id):
    try:
        with engine.connect() as conn:
            result = conn.execute(
            text("SELECT * FROM jobs WHERE id = :val"),
            {"val": id}
    )
            row = result.mappings().fetchone()
            return dict(row) if row else None
    except Exception as e:
        print(f"Error occurred while loading job with id {id}: {e}")
        return None
