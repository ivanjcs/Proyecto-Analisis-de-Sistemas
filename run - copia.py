from flask import Flask, render_template, request, redirect, url_for, flash
from forms import SignupForm, ProductForm, SearchForm,LoginForm
from gencodigo import generar_codigo
from db import insert_data
from flask_login import LoginManager, logout_user, current_user, login_user, login_required
from models import get_user_by_email, User
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="maestro",
    password="maestro123",
    database="tienda",
)
cursor = mydb.cursor()

app = Flask(__name__)
app.config['SECRET_KEY'] = '6a50272742e4b46149d7694375e64d952ddce526'
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    print(f"Cargando usuario: {user}")
    return user

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


@app.route("/admin/product/", methods=["GET","POST"], defaults = {'product_id': None})
@app.route("/admin/product/<int:post_id>/", methods=["GET","POST"]) 
@login_required
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

    return render_template("admin/edit_product.html", form=form)
    

@app.route("/admin/product/delete/<int:product_id>/", methods=["GET"])
def delete_product(product_id):
    delete_query = "DELETE FROM Producto WHERE id = %s"
    cursor.execute(delete_query, (product_id,))
    mydb.commit()

    flash("Producto eliminado exitosamente", "success")
    return redirect(url_for("index"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = get_user_by_email(email)
        if user is not None and user.check_password(password):
            login_user(user, remember=form.remember_me.data)
            flash("Inicio de sesión exitoso.", "success")
            next_page = request.args.get('next', None)
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash("Credenciales inválidas. Inténtelo nuevamente.", "danger")
    
    return render_template('login_form.html', form=form)



@login_manager.user_loader
def load_user(user_id):
    for user in users: 
        if user.id == int(user_id):
            return user
    return None

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))