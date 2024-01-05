import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="prisme_home_1"
)

# faire quelque chose d'utile avec la connexion
if db.is_connected():
    print("connexion établie")

db.close()
