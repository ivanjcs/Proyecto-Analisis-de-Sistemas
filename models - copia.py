from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="maestro",
    password="maestro123",
    database="tienda",
)
cursor = mydb.cursor()

class User(UserMixin):
    def __init__(self, id, name, email, password, is_admin=False):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.is_Active = True
    def check_password(self, password):
        # Comparar la contraseña proporcionada con la almacenada en la base de datos
        print(password)
        return check_password_hash(self.password, password)

def get_user_by_email(email):
    # Cambia esta función para que obtenga un usuario de la base de datos
    query = "SELECT * FROM Empleado2 WHERE correo = %s"
    cursor.execute(query, (email,))
    empleado_data = cursor.fetchone()

    if empleado_data:
        id, nombre, apellido, correo, password = empleado_data
        print(id, nombre, apellido, correo, password)
        return User(id, f"{nombre} {apellido}", correo, password)  # Concatenamos nombre y apellido para el campo 'name'
    return None