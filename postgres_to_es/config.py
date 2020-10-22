import os
from dotenv import load_dotenv

load_dotenv()

postgres_dsl = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

ETL_URL = os.getenv('ETL_URL')
