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
        sql_query = "SELECT * FROM Producto WHERE id LIKE %s;"
        cursor.execute(sql_query, (search_query,))
        result = cursor.fetchall()
    else:
        sql_query = "SELECT * FROM Producto"
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
        return redirect(url_for('index'))
    return render_template("admin/product_form.html", form=form)

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
@app.route("/admin/product/venta/<int:product_id>/", methods=["GET"])
def venta_product(product_id):
    """
    delete_query = "DELETE FROM Producto WHERE id = %s"
    cursor.execute(delete_query, (product_id,))
    mydb.commit()
    """
    
    flash("Producto vendido exitosamente", "success")
    return redirect(url_for("index"))
# termina producto


# empieza ventas
@app.route("/admin/ventas/", methods=['GET', 'POST'])
@login_required
def ventas():
    search_form = SearchForm()
    result = [] 
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
    

# termina ventas



# empieza registrarse
@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    #if current_user.is_authenticated:
    #    return redirect(url_for('index'))
    form = SignupForm()
    if form.validate_on_submit():
        apellido = form.apellido.data
        name = form.name.data
        email = form.email.data
        password = form.password.data
        # Creamos el usuario y lo guardamos
        user = User(name, apellido, email, password)
        #ingresa al usuario a la base de datos
        insert_data2(name,apellido,email,password)
        # Dejamos al usuario logueado
        login_user(user, remember=True)
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("signup_form.html", form=form)


##holaaaa
# termina registrarse

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        sql_query = "SELECT * FROM Empleado2 WHERE correo = %s"
        cursor.execute(sql_query, (form.email.data,))
        user_data = cursor.fetchone()

        if user_data:
            user = User(id=user_data[0], name=user_data[1], apellido=user_data[2], email=user_data[3], password=user_data[4])
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


