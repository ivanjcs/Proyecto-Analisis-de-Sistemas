from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, flash
from forms import SignupForm, ProductForm, SearchForm, LoginForm
from gencodigo import generar_codigo
from db import insert_data, insert_data2
from flask_login import LoginManager, logout_user, current_user, login_user, login_required
from models import User
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="ivan",
    password="maestro123",
    database="tienda",
    auth_plugin='mysql_native_password',
)
cursor = mydb.cursor()

app = Flask(__name__)
app.config['SECRET_KEY'] = '6a50272742e4b46149d7694375e64d952ddce526'
login_manager = LoginManager(app)
login_manager.login_view = "login"
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    search_form = SearchForm()
    result = [] 

    if search_form.validate_on_submit():
        search_query = f"%{search_form.search_query.data}"
        sql_query = "SELECT * FROM Producto WHERE id LIKE %s AND vendido = 0;"
        cursor.execute(sql_query, (search_query,))
        result = cursor.fetchall()
    else:
        sql_query = "SELECT * FROM Producto WHERE vendido = 0;"
        cursor.execute(sql_query)
        result = cursor.fetchall()

    return render_template("index.html", products=result, search_form=search_form)
# Resto del código...



# empieza producto
@app.route("/admin/product/", methods=["GET","POST"], defaults = {'product_id': None})
@app.route("/admin/product/<int:post_id>/", methods=["GET","POST"]) 
def product_form(product_id=None):
    form = ProductForm()
    form.codigo.data = generar_codigo()
    if form.validate_on_submit():
        try:
            name = form.name.data
            descripcion = form.descripcion.data
            precio = form.precio.data
            talle = form.talle.data
            fechaingreso = form.fechaingreso.data
            cantidad = form.cantidad.data
            codigo = form.codigo.data

            insert_data(codigo, name, descripcion, precio, talle, fechaingreso, cantidad)
            mydb.commit()
            product = {'name': name, 'descripcion': descripcion, 'precio': precio, 'talle': talle, 'fecha': fechaingreso, 'cantidad': cantidad, 'codigo': codigo}
        except mysql.connector.IntegrityError:
            flash("Error: El código del producto ya existe.", "danger")
        return redirect(url_for('index'))
    return render_template("admin/product_form.html", form=form)

@app.route("/admin/product/", methods=["POST"])
def add_product():
    try:
        codigo = request.form.get("codigo")
        nombre = request.form.get("nombre")
        # Otros datos del formulario...
        
        insert_query = "INSERT INTO Producto (codigo, nombre, descripcion, precio, talle, fechaingreso, cantidad) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (codigo, nombre, descripcion, precio, talle, fechaingreso, cantidad))
        mydb.commit()
        flash("Producto agregado exitosamente", "success")
    except mysql.connector.IntegrityError:
        flash("Error: El código del producto ya existe.", "danger")
    return redirect(url_for("index"))
# editar
@app.route("/admin/product/edit/<int:product_id>/", methods=["GET", "POST"])
def edit_product(product_id):
    form = ProductForm()
    if request.method == "GET":
        sql_query = "SELECT * FROM Producto WHERE id = %s"
        cursor.execute(sql_query, (product_id,))
        product_data = cursor.fetchone()
        #DEFINIMOS LOS PARAMETROS
        form.codigo.data = product_data[0]
        form.name.data = product_data[1]
        form.descripcion.data = product_data[2]
        form.precio.data = product_data[3]
        form.talle.data = product_data[4]
        form.fechaingreso.data = product_data[5]
        form.cantidad.data = product_data[6]

    if form.validate_on_submit():
        #ACTUALIZAMOS
        name = form.name.data
        descripcion = form.descripcion.data
        precio = form.precio.data
        talle = form.talle.data
        fechaingreso = form.fechaingreso.data
        cantidad = form.cantidad.data
        
        update_query = (
            "UPDATE Producto SET nombre=%s, descripcion=%s, precio=%s, talle=%s, fechaingreso=%s, cantidad=%s WHERE id=%s"
        )
        cursor.execute(
            update_query,
            (name, descripcion, precio, talle, fechaingreso, cantidad, product_id),
        )
        mydb.commit()

        flash("Producto actualizado exitosamente", "success")
        return redirect(url_for("index"))

    return render_template("admin/product_form.html", form=form)

# eliminar
@app.route("/admin/product/delete/<int:product_id>/", methods=["GET"])
def delete_product(product_id):
    delete_query = "DELETE FROM Producto WHERE id = %s"
    cursor.execute(delete_query, (product_id,))
    mydb.commit()

    flash("Producto eliminado exitosamente", "success")
    return redirect(url_for("index"))

# venta
"""
@app.route("/admin/product/venta/<int:product_id>/<int:employee_id>/<int:quantity>", methods=["GET"])
def venta_product(product_id, employee_id, quantity):
    print("Ruta activada: /admin/product/venta/{}".format(product_id))
    delete_query = "DELETE FROM Producto WHERE id = %s"
    cursor.execute(delete_query, (product_id,))
    mydb.commit()
    if request.method == "GET":
        print("Método get recibido")
        
        print("Datos de la venta recibidos:")
        print(f"Empleado ID: {employee_id}")
        print(f"Producto ID: {product_id}")
        print(f"Cantidad: {quantity}")

        # Validar los datos de entrada
        if not employee_id or not product_id or not quantity:
            print("Por favor, complete todos los campos", "error")
            return redirect(url_for("ventas", product_id=product_id))

        try:
            quantity = int(quantity)
        except ValueError:
            print("La cantidad debe ser un número entero", "error")
            return redirect(url_for("ventas", product_id=product_id))

        # Mostrar datos de la venta en la terminal

        # Insertar la venta en la base de datos
        insert_sale_query = (
            "INSERT INTO Venta (employee_id, product_id, quantity, date) "
            "VALUES (%s, %s, %s, NOW())"
        )
        cursor.execute(insert_sale_query, (employee_id, product_id, quantity))
        mydb.commit()

        flash("Venta registrada exitosamente", "success")
        return redirect(url_for("index"))

    # Manejar solicitudes GET u otros escenarios
    return redirect(url_for("index"))

""" 
@app.route("/admin/product/venta/<int:product_id>/<int:employee_id>/<int:quantity>", methods=["GET"])
def venta_product(product_id, employee_id, quantity):
    print("Ruta activada: /admin/product/venta/{}".format(product_id))
    
    if request.method == "GET":
        print("Método GET recibido")

        print("Datos de la venta recibidos:")
        print(f"Empleado ID: {employee_id}")
        print(f"Producto ID: {product_id}")
        print(f"Cantidad: {quantity}")

        # Validar los datos de entrada
        if not employee_id or not product_id or not quantity:
            print("Por favor, complete todos los campos", "error")
            return redirect(url_for("ventas", product_id=product_id))

        try:
            quantity = int(quantity)
        except ValueError:
            print("La cantidad debe ser un número entero", "error")
            return redirect(url_for("ventas", product_id=product_id))

        # Insertar la venta en la base de datos
        insert_sale_query = (
            "INSERT INTO Venta (employee_id, product_id, quantity, date) "
            "VALUES (%s, %s, %s, NOW())"
        )
        cursor.execute(insert_sale_query, (employee_id, product_id, quantity))
        mydb.commit()

        # Marcar el producto como vendido (no lo eliminamos, solo actualizamos el estado)
        update_product_query = "UPDATE Producto SET vendido = 1 WHERE id = %s"
        cursor.execute(update_product_query, (product_id,))
        mydb.commit()

        flash("Venta registrada exitosamente", "success")
        return redirect(url_for("index"))
    
    return redirect(url_for("index"))

@app.route('/venta/delete/<int:venta_id>', methods=['POST'])
@login_required
def delete_venta(venta_id):
    """Eliminar una venta"""
    try:
        # Recuperar la cantidad y producto de la venta antes de eliminar
        select_query = "SELECT product_id, quantity FROM Venta WHERE id = %s"
        cursor.execute(select_query, (venta_id,))
        venta = cursor.fetchone()

        if not venta:
            flash("Venta no encontrada", "error")
            return redirect(url_for('ventas'))

        product_id, quantity = venta

        # Eliminar la venta
        delete_query = "DELETE FROM Venta WHERE id = %s"
        cursor.execute(delete_query, (venta_id,))
        mydb.commit()

        # Restaurar el stock del producto
        update_stock = "UPDATE Producto SET cantidad = cantidad + %s WHERE id = %s"
        cursor.execute(update_stock, (quantity, product_id))
        mydb.commit()

        flash("Venta eliminada exitosamente", "success")
    except Exception as e:
        mydb.rollback()
        flash(f"Error al eliminar la venta: {str(e)}", "error")

    return redirect(url_for('ventas'))

# termina producto


# empieza ventas
@app.route("/admin/ventas/", methods=['GET', 'POST'])
@login_required
def ventas():
    search_form = SearchForm()
    
    if search_form.validate_on_submit():
        search_query = f"%{search_form.search_query.data}"
        sql_query = "SELECT * FROM Venta WHERE id LIKE %s;"  # Cambiar la consulta para obtener datos de ventas
        cursor.execute(sql_query, (search_query,))
        result = cursor.fetchall()
    else:
        sql_query = "SELECT * FROM Venta"  # Cambiar la consulta para obtener datos de ventas
        cursor.execute(sql_query)
        result = cursor.fetchall()
    return render_template("admin/ventas.html", ventas=result, search_form=search_form)
"""
    if search_form.validate_on_submit():
        search_query = f"%{search_form.search_query.data}"
        sql_query = "SELECT * FROM Ventas WHERE id LIKE %s;"  # Cambiar la consulta para obtener datos de ventas
        cursor.execute(sql_query, (search_query,))
        result = cursor.fetchall()
    else:
        sql_query = "SELECT * FROM Ventas"  # Cambiar la consulta para obtener datos de ventas
        cursor.execute(sql_query)
        result = cursor.fetchall()
"""
    
    
@app.route("/register_sale", methods=["GET", "POST"])
@login_required
def register_sale():
    if request.method == "POST":
        employee_id = request.form.get("employee_id")
        product_id = request.form.get("product_id")
        quantity = request.form.get("quantity")

        print(employee_id, product_id, quantity)
        # Inserta la venta en la base de datos
        insert_sale_query = (
            "INSERT INTO Venta (employee_id, product_id, quantity, date) "
            "VALUES (%s, %s, %s, NOW())"
        )
        cursor.execute(insert_sale_query, (employee_id, product_id, quantity))
        mydb.commit()

        flash("Venta registrada exitosamente", "success")
        return redirect(url_for("index"))
    return render_template("ventas.html")

# termina ventas

@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    form = SignupForm()
    if form.validate_on_submit():
        apellido = form.apellido.data
        name = form.name.data
        email = form.email.data
        password = form.password.data

        print(password)
        # Crear el usuario con un ID temporal (esto puede variar según cómo manejes los IDs en la base de datos)
        user = User(id=None, name=name, apellido=apellido, email=email, password=password)

        # Ahora puedes guardar el usuario en la base de datos
        # Es posible que quieras generar el ID después de insertar el usuario en la base de datos
        insert_data2(name, apellido, email, password)  # Asume que la función `insert_data2` maneja la inserción correctamente

        # Dejamos al usuario logueado
        login_user(user, remember=True)

        # Redirigir al usuario a la página principal o a la página anterior
        next_page = request.args.get('next', None)
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template("signup_form.html", form=form)



"""
@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    form = SignupForm()
    if form.validate_on_submit():
        apellido = form.apellido.data
        name = form.name.data
        email = form.email.data
        password = form.password.data

        print(apellido)
        # Crear el usuario con un ID temporal (esto puede variar según cómo manejes los IDs en la base de datos)
        user = User(id=None, name=name, apellido=apellido, email=email, password=password)

        # Ahora puedes guardar el usuario en la base de datos
        # Es posible que quieras generar el ID después de insertar el usuario en la base de datos
        insert_data2(name, apellido, email, user.password)  # Asume que la función `insert_data2` maneja la inserción correctamente

        # Dejamos al usuario logueado
        login_user(user, remember=True)

        # Redirigir al usuario a la página principal o a la página anterior
        next_page = request.args.get('next', None)
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template("signup_form.html", form=form)
"""
##holaaaa
# termina registrarse

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        sql_query = "SELECT * FROM Empleado2 WHERE correo = %s"
        try:
            cursor.execute(sql_query, (form.email.data,))
            user_data = cursor.fetchall()
        except mysql.connector.Error as err:
            # Handle database error (e.g., log the error)
            return render_template('error.html', message=str(err))

        if user_data:
            user = User(id=user_data[0][0], name=user_data[0][1], apellido=user_data[0][2], email=user_data[0][3], password=user_data[0][4])
            if user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next', None)
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('index')
                return redirect(next_page)

    return render_template('login_form.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    sql_query = "SELECT * FROM Empleado2 WHERE id = %s"
    cursor.execute(sql_query, (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        user = User(id=user_data[0], name=user_data[1], apellido=user_data[2], email=user_data[3], password=user_data[4])
        return user
    return None

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


