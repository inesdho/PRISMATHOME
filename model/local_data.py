import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="prismathome"
)

# faire quelque chose d'utile avec la connexion
if db.is_connected():
    print("connexion établie")

db.close()
