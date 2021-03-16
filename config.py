import os
from dotenv import load_dotenv

#load_dotenv() will first look for a .env file and if it finds one, 
# it will load the environment variables from the file and make them 
# accessible to your project like any other environment variable would be.
load_dotenv()


class Config:
    """Set Flask config variables."""

    SECRET_KEY = os.getenv('SECRET_KEY')
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT'))
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB = os.getenv('MYSQL_DB')