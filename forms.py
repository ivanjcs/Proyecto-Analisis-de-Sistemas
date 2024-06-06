from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class SignupForm(FlaskForm):
    name = StringField('Nombre', validators = [DataRequired(), Length(max=64)])
    apellido = StringField('Apellido', validators = [DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Registrar')
    #DataRequired = verifica que no se dejen vacios
    #Length restringe su longitud
    #Email verifica que es un email.

class SearchForm(FlaskForm):
    search_query = StringField('Buscar producto: ')
    submit = SubmitField('Buscar')
class ProductForm(FlaskForm):
    name = StringField('Nombre del producto', validators = [DataRequired(), Length (max=20)])
    descripcion = StringField('Descripcion', validators = [DataRequired(), Length(max =120)])
    precio = IntegerField('Precio', validators=[DataRequired()])
    talle = StringField('Talle', validators = [DataRequired()])
    fechaingreso = DateField('Fecha de ingreso', format='%Y-%m-%d', validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired()])
    submit = SubmitField('Cargar producto')
    codigo = StringField('Código')
    submit_edit = SubmitField('Editar producto')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')