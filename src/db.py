import mysql.connector
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",         # Database Username
        password="Bao200304", # Database password
        database="paragon_db"
    )