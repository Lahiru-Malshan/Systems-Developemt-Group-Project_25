import mysql.connector
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",         # Database Username
        password="HELLOWORLD", # Database password
        database="systems_project"
    )