import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="ivan",
    password="maestro123",
    database="tienda",
    auth_plugin='mysql_native_password',
)
cursor = mydb.cursor() #objeto que permite la conexion entre la base sql y el archivo
menu = True

def view_data():
    sql_query = "select * from Producto"
    cursor.execute(sql_query)
    result = cursor.fetchall() #trae esta consulta

def insert_data(id, nombre, descripcion, precio, talle, fechaingreso, cantidad):
    # verificar si el id ya existe en la tabla
    check_query = "SELECT COUNT(*) FROM Producto WHERE id = %s"
    cursor.execute(check_query, (id,))
    result = cursor.fetchone()

    if result[0] == 0:
        #si el id existe
        sql_query = """ 
        INSERT INTO Producto (id, nombre, descripcion, precio, talle, fechaingreso, cantidad) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (id, nombre, descripcion, precio, talle, fechaingreso, cantidad)
        cursor.execute(sql_query, values)
        mydb.commit()
        print("Producto añadido correctamente.")
    else:
        print("Error: El ID ya existe en la tabla.")


def insert_data2(nombre, apellido, correo, contraseña):
    check_query = "SELECT COUNT(*) FROM Empleado2 WHERE correo = %s"
    cursor.execute(check_query, (correo,))
    result1 = cursor.fetchone()
    
    if result1[0] == 0:
        sql_query = "insert into Empleado2(nombre, apellido, correo, contraseña) values (%s,%s,%s,%s)"
        values = (nombre, apellido, correo, contraseña)#SON SIEMPRE DEL TIPO TUPLA
        cursor.execute(sql_query, values)
        print("Usuario añadido correctamente.")
    else:
        print("Error: El correo ya existe.")
    mydb.commit()

def find_id_data():
    sql_query = "select id from usuario where username = %s"
    username = input("Ingrese el nombre del usuario a eliminar: ")
    values = (username, ) #SIEMPRE DEL TIPO TUPLA
    cursor.execute(sql_query, values)
    id = cursor.fetchone()
    return id

def delete_data():
    id = find_id_data()
    sql_query = "delete from usuario where id = %s"
    cursor.execute(sql_query, id)
    mydb.commit()

"""
while menu:
    option = int(input("Seleccione la opcion a realizar: 1- Ver 2- Insertar: 3- Eliminar  "))
    if option ==1:
        view_data()
    elif option ==2:
        insert_data(12, "hola", "beuans", 12000, "XL", '1990-10-23', 9)
    elif option ==3:
        delete_data()
    else:
        menu = False
"""