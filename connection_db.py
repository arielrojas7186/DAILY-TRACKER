import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

db_password = os.getenv('DATABASE_PASSWORD')




def initialize_connection():
    conn= psycopg2.connect(
        host = "localhost",
        port = 5432,
        dbname= "daily_tracker",
        user= 'postgres',
        password= db_password
    )

    return conn