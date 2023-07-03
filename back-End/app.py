from flask import Flask, jsonify, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, text
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from wtforms import *
from wtforms.validators import *
from rutas import *
from clases import *
from sqlalchemy.orm import joinedload


login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(cedula):
    return User.query.get(int(cedula))

@app.route('/')
@app.route('/home.html')
def index():
    usuarios = User.query.all()
    return render_template("/noLog/home.html", usuarios=usuarios)

@app.route('/')
@app.route('/edit/home.html')
def editindex():
    usuarios = User.query.all()
    return render_template("/noLog/home.html", usuarios=usuarios)

@app.route('/registerform', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            cedula = form.cedula.data
            name = form.name.data
            telefono =form.telefono.data
            email = form.email.data        
            user = User.query.filter(or_(
                User.cedula == cedula, User.name == name, User.telefono == telefono, User.email == email)).first()
            if user:
                return redirect(url_for('miembros'))
            new_user = User(cedula=cedula, name=name,
                            telefono=telefono, email=email)
            db.session.add(new_user)
            db.session.commit()    
        return redirect(url_for('miembros'))
    return redirect(url_for('miembros', form=form))

@app.route('/edit/miembros.html')
def editmiembros():
    form = RegistrationForm()
    usuarios = User.query.all()
    return render_template('/logueado/miembros.html',form=form, users=usuarios)

# FUNCION QUE SE ENCARGARA DE ELIMINAR SOCIOS DEL CLUB // FUNCIONA
@app.route('/delete/<cedula>')
def delete_socio(cedula):
    socio = User.query.filter_by(cedula=cedula).first()

    if socio:
        db.session.delete(socio)
        db.session.commit()
    
    return redirect(url_for('miembros'))

@app.route('/edit/<cedula>', methods=['GET', 'POST'])
def editar_usuario(cedula):
    form = EditForm(obj=User)
    usuario = User.query.get_or_404(cedula)
    if form.validate_on_submit():
        usuario.cedula = form.cedula.data
        usuario.name = form.name.data
        usuario.telefono =form.telefono.data
        usuario.email = form.email.data
        db.session.commit()
        return redirect(url_for('miembros'))

    return render_template('/logueado/edit_usuario.html', form=form, usuario=usuario)

@app.route('/registerplanta', methods=['GET', 'POST'])
def registerplanta():
    form = PlantForm()
    if request.method == "POST":
        if form.validate_on_submit():  
            trazabilidad = Trazabilidad.query.order_by(Trazabilidad.idplanta.desc()).first()
            if trazabilidad:
                new_idplanta = trazabilidad.idplanta + 1
            else:
                new_idplanta = 1
            raza = form.raza.data
            Enraizado = form.Enraizado.data
            Riego = form.Riego.data
            paso1 = form.paso1.data
            paso2 = form.paso2.data
            paso3 = form.paso3.data
            floracion = form.floracion.data
            cosecha = form.cosecha.data
            cantidad = int(form.cantidad.data.replace(',', ''))
            observaciones = form.observaciones.data
            new_planta = Trazabilidad(idplanta=new_idplanta, raza=raza, Enraizado=Enraizado, Riego=Riego,
                                       paso1=paso1, paso2=paso2, paso3=paso3, floracion=floracion,
                                       cosecha=cosecha, cantidad=cantidad, observaciones=observaciones)
            db.session.add(new_planta)
            db.session.commit()
        return redirect(url_for('trazabilidad'))
    return render_template('/logueado/trazabilidad.html', form=form)

@app.route('/delete/<idRaza>')
def delete_planta(idRaza):
    elimplanta = User.query.filter_by(idRaza=idRaza).first()
  
    if elimplanta:
        db.session.delete(elimplanta)
        db.session.commit()
  
    return redirect(url_for('homeplantcreo'))

##########################################################################################################################################
@app.route('/ventas', methods=['GET', 'POST'])
def ventosa():
    form = Ventasform()
    nueva_venta = Ventas.query.order_by(Ventas.idventas.desc()).first().idventas + 1
    cedula = form.cedula.data
    raza = form.raza.data
    cantidad = form.cantidad.data
    retiro = form.retiro.data
    usuario = User.query.filter_by(cedula=cedula).first()
    if usuario:
            # Verifica si el usuario ha superado el límite de cantidad de compras
        if usuario.total_ventas + cantidad > 40:
            flash("alerta de compra eccedida")
            return redirect(url_for('otra_pagina'))
        usuario.total_ventas += cantidad        
        new_venta = Ventas(idventas=nueva_venta, cedula=cedula, raza=raza, cantidad=cantidad,
                                    retiro=retiro,)
        db.session.add(new_venta)
        db.session.commit()
        return redirect(url_for('otra_pagina')) 
  
    return render_template('registerplanta.html', form=form)

# #########################################################################################################################################################


@app.route('/tabla_ventas')
def tabla_datos():
    datos = obtener_datos()
    return render_template('ventas.html', datos=datos)
def obtener_datos():
    datos = db.session.query(Ventas.idventas, Ventas.cedula, Ventas.raza, Ventas.cantidad, Ventas.retiro).join(User).join(Trazabilidad).all()
    return datos

# #########################################################################################################################################################
@app.route('/prueba', methods=['GET', 'POST'])
def obDatosU():
    users = User.query.all()

    # Crear una lista para almacenar los datos de los usuarios
    users_data = []
    for user in users:
        user_data = {
            'cedula': user.cedula,
            'name': user.name,
            'telefono': user.telefono,
            'email': user.email
        }
        users_data.append(user_data)

    # Devolver los datos de los usuarios en formato JSON
    return jsonify(users_data)
# #############################################################################################################################################
# def obtenemos():
#     atos = db.session.query(Ventas.idventas, User.cedula, Trazabilidad.raza, Ventas.cantidad, Ventas.retiro).join(User).join(Trazabilidad).all()
#     datos_dict = [{'idventas': ato.idventas, 'cedula': ato.cedula, 'raza': ato.raza, 'cantidad': ato.cantidad, 'retiro': ato.retiro,} for ato in atos]
#     return datos_dict



# @app.route('/datos')
# def mostrar_datos():
#     datos = obtenemos()
#     return render_template('ventas.html', datos=datos)

# ##############################################################################################################################################






# @app.route('/contact.html')
# def contact():
#     return render_template('/noLog/contact.html')


@app.route('/login.html')
def login():
    form = LoginForm
    return render_template('/noLog/login.html', form=form)

@app.route('/edit/login.html')
def editlogin():
    form = LoginForm
    return render_template('/noLog/login.html', form=form)

# @app.route('/nosotros.html')
# def nosotros():
#     return render_template('/noLog/nosotros.html')

# @app.route('/equipo.html')
# def equipo():
#     return render_template('/noLog/equipo.html')

# @app.route('/road-map.html')
# def roadMap():
#     return render_template('/noLog/road-map.html')

# @app.route('/home-club.html')
# def home_club():
#     return render_template('/logueado/home-club.html')



@app.route('/ventas.html')
def ventas():
    return render_template('/logueado/ventas.html')
@app.route('/edit/ventas.html')
def editventas():
    return render_template('/logueado/ventas.html')

@app.route('/trazabilidad.html')
def trazabilidad():
    form = PlantForm()
    return render_template('/logueado/trazabilidad.html', form=form)
@app.route('/edit/trazabilidad.html')
def edittrazabilidad():
    form = PlantForm()
    return render_template('/logueado/trazabilidad.html', form=form)

@app.route('/edit/ctrplanta.html')
def editctrplanta():
    return render_template('/logueado/ctrplanta.html')
@app.route('/ctrplanta.html')
def ctrplanta():
    return render_template('/logueado/ctrplanta.html')

@app.route('/graficos.html')
def graficos():
    return render_template('/logueado/graficos.html')
@app.route('/edit/graficos.html')
def editgraficos():
    return render_template('/logueado/graficos.html')






























# Es importante tener en cuenta que, para que el formulario se muestre correctamente en la vista, es necesario
# renderizarlo usando una plantilla de Jinja2 y agregar el atributo enctype="multipart/form-data" al formulario para permitir la carga de archivos.


# @app.route('/register', methods=['GET', 'POST'])
# def clubes():
#     form = ClubForm()

#     if form.validate_on_submit():

#       # procesa el formulario y guarda los datos en la base de datos

#         # Si todo va bien, redirige a otra página que seria la del registro del club como puede ser el login
#         return redirect(url_for('otra_pagina'))

#     # Si hay algún error en la validación del formulario, muestra una SweetAlert como la de arriba
#     errors = form.errors.items()
#     if errors:
#         response = jsonify({'message': 'El usuario ya existe'})
#         response.headers['Fail-SweetAlert'] = 'error'
#         return render_template('clubes.html', form=form)



# @app.route('/loginform', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         nombre = request.form['nombre']  # Obtiene el valor del campo "nombre"
#     edad = request.form['edad'] 

#     if request.method == 'POST':
#         print(request.form['username'])
#         print(request.form['password'])
#         return render_template('login.html')
#     else:
#         return render_template('login.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)