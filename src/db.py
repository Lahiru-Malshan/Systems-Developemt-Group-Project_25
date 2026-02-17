import mysql.connector
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",         # Database Username
        password="TrunTrun_TramCam3004", # Database password
        database="paragon_db"
    )