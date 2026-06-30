from flask import Flask, render_template, request,redirect, url_for, flash  # <--- Asegúrate de agregar , render_template aquí
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
import MySQLdb.cursors 
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta_super_segura_para_las_sesiones' #

# Inicializamos el manejador de inicios de sesión
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Indica a dónde redirigir si no están logueados

mysql=MySQL()

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_PORT']= 3306
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='residencias'
mysql.init_app(app)
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirecciona acá si intentan entrar sin permiso

# 2. Clase de Usuario que necesita Flask-Login para manejar la sesión
class Usuario(UserMixin):
    # Al ponerle =None, si no le pasás la sede, asume None en lugar de tirar error
    def __init__(self, id, nombre, correo,nivel, sede):  
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.nivel  = nivel
        self.sede   = sede
        
# 3. Función clave: Carga al usuario desde la base de datos usando su ID
@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    # Forzamos que traiga las columnas en este orden exacto
    cursor.execute("SELECT id, nombre, correo, nivel, sede FROM usuarios WHERE id = %s", (user_id,))
    usuario_db = cursor.fetchone()
    cursor.close()
    
    if usuario_db:
        # Esto te va a mostrar en la terminal si es una tupla o diccionario
        print("🔍 RASTREO DB ->", usuario_db)
        
        # Mapeo posicional directo: 0=id, 1=nombre, 2=correo, 3=sede
        return Usuario(usuario_db['id'], usuario_db['nombre'], usuario_db['correo'], usuario_db['nivel'], usuario_db['sede'])
        
    return None 



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
        usuario_db = cursor.fetchone()
        cursor.close()
        # Validar contraseña con hash
        if usuario_db and check_password_hash(usuario_db['password'], password):
            user_obj = Usuario(
                usuario_db['id'],
                usuario_db['nombre'],
                usuario_db['correo'],
                usuario_db['nivel'],
                usuario_db['sede']
            )
            login_user(user_obj)

            # 🔑 Redirección según nivel (dentro de la función)
            if user_obj.nivel == 1:
                return redirect(url_for('gestionar_usuarios'))
            elif user_obj.nivel == 2:
                return redirect(url_for('index'))
            elif user_obj.nivel == 3:
                return redirect(url_for('consulta'))
            else:
                flash('Nivel de usuario no reconocido', 'warning')
                return redirect(url_for('login'))

        flash('Correo o contraseña incorrectos', 'danger')
    return render_template('/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user() # Borra la sesión
    return redirect(url_for('login'))


@app.route('/cambiar_clave', methods=['GET', 'POST'])
@login_required
def cambiar_clave():
    if request.method == 'POST':
        clave_actual = request.form['clave_actual']
        nueva_clave = request.form['nueva_clave']
        confirmar_clave = request.form['confirmar_clave']

        cursor = mysql.connection.cursor()
        
        # 1. Buscamos el hash de la contraseña actual del usuario logueado
        cursor.execute("SELECT password FROM usuarios WHERE id = %s", (current_user.id,))
        usuario_db = cursor.fetchone()
        
        # 2. Verificamos que la clave actual ingresada coincida con la de la base de datos
        if not usuario_db or not check_password_hash(usuario_db['password'], clave_actual):
            flash('La contraseña actual es incorrecta.', 'danger')
            cursor.close()
            return redirect(url_for('cambiar_clave'))

        # 3. Verificamos que las contraseñas nuevas sean iguales
        if nueva_clave != confirmar_clave:
            flash('Las contraseñas nuevas no coinciden.', 'danger')
            cursor.close()
            return redirect(url_for('cambiar_clave'))

        # 4. Encriptamos la nueva contraseña y actualizamos el registro
        nuevo_hash = generate_password_hash(nueva_clave)
        cursor.execute("UPDATE usuarios SET password = %s WHERE id = %s", (nuevo_hash, current_user.id))
        mysql.connection.commit() # Importante: ¡guardar los cambios!
        cursor.close()
        
        flash('Tu contraseña ha sido actualizada exitosamente.', 'success')
        return redirect(url_for('index')) # Asumo que 'index' es tu panel principal

    # Petición GET: mostramos el formulario
    return render_template('cambiar_clave.html')


@app.route('/')
def index():
    # Esto le dice a Flask que vaya a buscar el archivo index.html dentro de 'templates'
    return render_template('index.html') 



@app.route('/reevaluaciones')  # <-- Agregamos la ruta que faltaba
@login_required # <-- SI NO ESTÁ LOGUEADO, NO ENTRA Y LO MANDA AL LOGIN
def index_reevaluaciones():
    sql = "SELECT * FROM REEVALUACIONES"
    
    connection = mysql.connection
    cursor = connection.cursor()
    cursor.execute(sql)
    reevaluaciones = cursor.fetchall()
    cursor.close()  # <-- Buena práctica: cerrar el cursor
    
    # Pasamos la variable al HTML para que la puedas iterar
    return render_template('/modulos/reevaluaciones/index.html', reevaluaciones=reevaluaciones)


@app.route('/reevaluaciones/create') 
@login_required #
def create():
    # 1. Abrimos el cursor para consultar la base de datos
    # Usamos dictionary=True (o el formato que maneje tu conector) para acceder fácil por nombre de columna
    cursor = mysql.connection.cursor(DictCursor) 
    
    # 2. Buscamos las opciones de CDPs (ajustá el nombre de tabla/columnas si varían en tu BD)
      
    cursor.execute("SELECT referente FROM referentes ORDER BY referente ASC")
    lista_cdps = cursor.fetchall()
    
    
    
    # 3. Buscamos las opciones de Especialidades
    cursor.execute("SELECT especialidad FROM especialidad ORDER BY especialidad ASC")
    lista_especialidades = cursor.fetchall()
    
    cursor.close()
    
    # 4. Renderizamos mandando las dos listas hacia el HTML
    return render_template(
        '/modulos/reevaluaciones/create.html', 
        cdps=lista_cdps, 
        especialidades=lista_especialidades
    )


@app.route('/reevaluaciones/guardar', methods=['POST'])
@login_required
def reevaluaciones_guardar():
    # Tu código actual se queda EXACTAMENTE IGUAL. 
    # request.form['referente'] y request.form['especialidad'] 
    # van a atrapar de forma automática la opción que el usuario haya elegido en el select.
    #usuario = current_user.nombre
    usuario                 = request.form['usuario']
    tipo_de_reevaluacion    = request.form['tipo_de_reevaluacion']
    expediente              = request.form['expediente']
    referente               = request.form['referente']
    fecha_envio_cdp         = request.form['fecha_envio_cdp']
    apellido_nombre_residente = request.form['apellido_nombre_residente']
    dni                     = request.form['dni']
    region_sanitaria        = request.form['region_sanitaria']
    sede                    = request.form['sede']
    especialidad            = request.form['especialidad']
    nivel                   = request.form['nivel']
    nivel_academico         = request.form['nivel_academico']
    anio_residencia         = request.form['anio_residencia']
    sede_reevaluacion       = request.form['sede_reevaluacion']
    tiempo_solicitado_reevaluacion_meses = request.form['tiempo_solicitado_reevaluacion_meses']
    fecha_inicio_reevaluacion = request.form['fecha_inicio_reevaluacion']
    fecha_finalizacion_reevaluacion = request.form['fecha_finalizacion_reevaluacion']
    incluye_extension_peri_de_residencia = request.form['incluye_extension_peri_de_residencia']
    cdp_evaluadora          = request.form['cdp_evaluadora']
    aceptada_cdp            = request.form['aceptada_cdp']
    observaciones_cdp       = request.form['observaciones_cdp']
    disposicion_de_aprobacion = request.form['disposicion_de_aprobacion']
    resultado_reevaluacion  = request.form['resultado_reevaluacion']
    observaciones           = request.form['observaciones']

    sql = """INSERT INTO reevaluaciones (
    usuario, tipo_de_reevaluacion, expediente, referente, 
    fecha_envio_cdp, apellido_nombre_residente, dni, region_sanitaria, 
    sede, especialidad, nivel,nivel_academico, anio_residencia, 
    sede_reevaluacion, tiempo_solicitado_reevaluacion_meses, fecha_inicio_reevaluacion, 
    fecha_finalizacion_reevaluacion, incluye_extension_peri_de_residencia, cdp_evaluadora, 
    aceptada_cdp, observaciones_cdp, disposicion_de_aprobacion, resultado_reevaluacion, 
    observaciones
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    connection = mysql.connection
    cursor = connection.cursor()
    cursor.execute(sql, (usuario, tipo_de_reevaluacion, expediente, referente, 
    fecha_envio_cdp, apellido_nombre_residente, dni, region_sanitaria, 
    sede, especialidad, nivel,nivel_academico, anio_residencia, 
    sede_reevaluacion, tiempo_solicitado_reevaluacion_meses, fecha_inicio_reevaluacion, 
    fecha_finalizacion_reevaluacion, incluye_extension_peri_de_residencia, cdp_evaluadora, 
    aceptada_cdp, observaciones_cdp, disposicion_de_aprobacion, resultado_reevaluacion, 
    observaciones))
    mysql.connection.commit()
    cursor.close()
    return redirect('/reevaluaciones')

@app.route('/modulos/reevaluaciones/edit/<int:id>')
@login_required
def reevaluaciones_edit(id):
    cursor = mysql.connection.cursor()
    
    # 1. Traemos los datos de la reevaluación que se va a editar
    cursor.execute("SELECT * FROM reevaluaciones WHERE id = %s", (id,))
    data_reevaluacion = cursor.fetchone()
    
    # 2. Traemos la lista completa de referentes para el select
    cursor.execute("SELECT referente FROM referentes ORDER BY referente ASC")
    lista_cdps = cursor.fetchall()
    
    # 3. Traemos la lista completa de especialidades para el select
    cursor.execute("SELECT especialidad FROM especialidad ORDER BY especialidad ASC")
    lista_especialidades = cursor.fetchall()
    
    cursor.close()
    
    # Pasamos todo al HTML
    return render_template(
        '/modulos/reevaluaciones/edit.html', 
        reevaluacion=data_reevaluacion, 
        cdps=lista_cdps, 
        especialidades=lista_especialidades
    )
@app.route('/modulos/reevaluaciones/actualizar/<int:id>', methods=['POST'])
@login_required
def reevaluaciones_actualizar(id):
    if request.method == 'POST':
        usuario = request.form['usuario']
        tipo_de_reevaluacion = request.form['tipo_de_reevaluacion']
        expediente = request.form['expediente']
        referente = request.form['referente']
        fecha_envio_cdp = request.form['fecha_envio_cdp']
        apellido_nombre_residente = request.form['apellido_nombre_residente']
        dni = request.form['dni']
        region_sanitaria = request.form['region_sanitaria']
        sede = request.form['sede']
        especialidad = request.form['especialidad']
        nivel = request.form['nivel']
        nivel_academico = request.form['nivel_academico']
        anio_residencia = request.form['anio_residencia']
        sede_reevaluacion = request.form['sede_reevaluacion']
        tiempo_solicitado_reevaluacion_meses = request.form['tiempo_solicitado_reevaluacion_meses']
        fecha_inicio_reevaluacion = request.form['fecha_inicio_reevaluacion']
        fecha_finalizacion_reevaluacion = request.form['fecha_finalizacion_reevaluacion']
        incluye_extension_peri_de_residencia = request.form['incluye_extension_peri_de_residencia']
        cdp_evaluadora = request.form['cdp_evaluadora']
        aceptada_cdp = request.form['aceptada_cdp']
        observaciones_cdp = request.form['observaciones_cdp']
        disposicion_de_aprobacion = request.form['disposicion_de_aprobacion']
        resultado_reevaluacion = request.form['resultado_reevaluacion']
        observaciones = request.form['observaciones']

        # La orden SQL con SET para modificar los campos existentes
        sql = """UPDATE reevaluaciones SET 
            usuario=%s, tipo_de_reevaluacion=%s, expediente=%s, referente=%s, 
            fecha_envio_cdp=%s, apellido_nombre_residente=%s, dni=%s, region_sanitaria=%s, 
            sede=%s, especialidad=%s, nivel=%s,nivel_academico=%s, anio_residencia=%s, 
            sede_reevaluacion=%s, tiempo_solicitado_reevaluacion_meses=%s, fecha_inicio_reevaluacion=%s, 
            fecha_finalizacion_reevaluacion=%s, incluye_extension_peri_de_residencia=%s, cdp_evaluadora=%s, 
            aceptada_cdp=%s, observaciones_cdp=%s, disposicion_de_aprobacion=%s, resultado_reevaluacion=%s, 
            observaciones=%s 
            WHERE id=%s"""

        cursor = mysql.connection.cursor()
        # Pasamos las 23 variables + el ID al final (en total 24 elementos)
        cursor.execute(sql, (
            usuario, tipo_de_reevaluacion, expediente, referente, 
            fecha_envio_cdp, apellido_nombre_residente, dni, region_sanitaria, 
            sede, especialidad, nivel, nivel_academico, anio_residencia, 
            sede_reevaluacion, tiempo_solicitado_reevaluacion_meses, fecha_inicio_reevaluacion, 
            fecha_finalizacion_reevaluacion, incluye_extension_peri_de_residencia, cdp_evaluadora, 
            aceptada_cdp, observaciones_cdp, disposicion_de_aprobacion, resultado_reevaluacion, 
            observaciones, id
        ))
        mysql.connection.commit()
        cursor.close()
        return redirect('/reevaluaciones')
    


@app.route('/reevaluaciones/borrar/<int:id>')
@login_required
def reevaluaciones_borrar(id):
    connection = mysql.connection
    cursor = connection.cursor()
    cursor.execute("DELETE FROM reevaluaciones WHERE id=%s", (id,))
    connection.commit()
    cursor.close()
    return redirect('/reevaluaciones')



@app.route('/prorrogas')
@login_required
def index_prorrogas():
    sql1 = "SELECT * FROM PRORROGAS"
    
    connection = mysql.connection
    cursor = connection.cursor()
    cursor.execute(sql1)
    prorrogas = cursor.fetchall()
    cursor.close()  # <-- Buena práctica: cerrar el cursor
    
    # Pasamos la variable al HTML
    return render_template('/modulos/prorrogas/index.html', prorrogas=prorrogas)


@app.route('/prorrogas/create')
@login_required
def prorrogas_create():
    cursor = mysql.connection.cursor()
    
    # Buscamos los referentes ordenados
    cursor.execute("SELECT referente FROM referentes ORDER BY referente ASC")
    lista_cdps = cursor.fetchall()
    # Buscamos las especialidades ordenadas
    cursor.execute("SELECT especialidad FROM especialidad ORDER BY especialidad ASC")
    lista_especialidades = cursor.fetchall()
    cursor.close()
    return render_template('/modulos/prorrogas/create.html', 
    cdps=lista_cdps, 
    especialidades=lista_especialidades)

@app.route('/modulos/prorrogas/guardar', methods=['POST'])
@login_required
def prorrogas_guardar():
    usuario	                = request.form['usuario']
    tipo_prorroga           = request.form['tipo_prorroga']
    nro_expediente          = request.form['nro_expediente']
    referente               = request.form['referente']
    fecha_envio_cdp         = request.form['fecha_envio_cdp']
    residente_nombre        = request.form['residente_nombre']
    dni                     = request.form['dni']
    region_sanitaria        = request.form['region_sanitaria']
    sede                    = request.form['sede']
    especialidad            = request.form['especialidad']
    nivel                   = request.form['nivel']
    nivel_academico         = request.form['nivel_academico']
    anio_residencia         = request.form['anio_residencia']
    meses_solicitados       = request.form['meses_solicitados']
    fecha_inicio            = request.form['fecha_inicio']
    fecha_fin               = request.form['fecha_fin']
    observaciones           = request.form['observaciones']
    cdp_evaluadora          = request.form['cdp_evaluadora']
    aceptada_cdp            = request.form['aceptada_cdp']
    observaciones_cdp       = request.form['observaciones_cdp']
    pv_aprobacion           = request.form['pv_aprobacion']
    fecha_notificacion      = request.form['fecha_notificacion']


    sql= """INSERT INTO prorrogas (usuario, tipo_prorroga, nro_expediente,
    referente,fecha_envio_cdp, residente_nombre, dni, region_sanitaria, 
    sede, especialidad, nivel,nivel_academico, anio_residencia,meses_solicitados,
    fecha_inicio,fecha_fin,observaciones, cdp_evaluadora, 
    aceptada_cdp, observaciones_cdp, pv_aprobacion, fecha_notificacion 
        
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
              %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s, %s ,%s)"""
    connection=mysql.connection
    cursor=connection.cursor()
    cursor.execute(sql,( usuario, tipo_prorroga,nro_expediente,referente,fecha_envio_cdp,
    residente_nombre, dni, region_sanitaria,sede, especialidad, nivel,nivel_academico, anio_residencia, 
    meses_solicitados, fecha_inicio, fecha_fin,observaciones, cdp_evaluadora, 
    aceptada_cdp, observaciones_cdp, pv_aprobacion, fecha_notificacion ))
    mysql.connection.commit()
    cursor.close()
    return redirect('/prorrogas')


@app.route('/modulos/prorrogas/edit/<int:id>')
@login_required
def prorrogas_edit(id):
    cursor = mysql.connection.cursor()
    
    # 1. Traemos los datos de la prórroga específica
    cursor.execute("SELECT * FROM prorrogas WHERE id = %s", (id,))
    data_prorroga = cursor.fetchone()
    
    # 2. Traemos los referentes para el select
    cursor.execute("SELECT referente FROM referentes ORDER BY referente ASC")
    lista_cdps = cursor.fetchall()
    
    # 3. Traemos las especialidades para el select
    cursor.execute("SELECT especialidad FROM especialidad ORDER BY especialidad ASC")
    lista_especialidades = cursor.fetchall()
    
    cursor.close()
    
    return render_template(
        '/modulos/prorrogas/edit.html', 
        prorroga=data_prorroga, 
        cdps=lista_cdps, 
        especialidades=lista_especialidades
    )  

@app.route('/modulos/prorrogas/actualizar/<int:id>', methods=['POST'])
@login_required
def prorrogas_actualizar(id):
    if request.method == 'POST':
        usuario	                = request.form['usuario']
        tipo_prorroga           = request.form['tipo_prorroga']
        nro_expediente          = request.form['nro_expediente']
        referente               = request.form['referente']
        fecha_envio_cdp         = request.form['fecha_envio_cdp']
        residente_nombre        = request.form['residente_nombre']
        dni                     = request.form['dni']
        region_sanitaria        = request.form['region_sanitaria']
        sede                    = request.form['sede']
        especialidad            = request.form['especialidad']
        nivel                   = request.form['nivel']
        nivel_academico         = request.form['nivel_academico']
        anio_residencia         = request.form['anio_residencia']
        meses_solicitados       = request.form['meses_solicitados']
        fecha_inicio            = request.form['fecha_inicio']
        fecha_fin               = request.form['fecha_fin']
        observaciones           = request.form['observaciones']
        cdp_evaluadora          = request.form['cdp_evaluadora']
        aceptada_cdp            = request.form['aceptada_cdp']
        observaciones_cdp       = request.form['observaciones_cdp']
        pv_aprobacion           = request.form['pv_aprobacion']
        fecha_notificacion      = request.form['fecha_notificacion']


    # La orden SQL con SET para modificar los campos existentes
    sql ="""UPDATE prorrogas SET usuario=%s, tipo_prorroga=%s, nro_expediente=%s, 
    referente=%s, fecha_envio_cdp=%s,residente_nombre=%s, dni=%s, 
    region_sanitaria=%s,sede=%s, especialidad=%s, nivel=%s,nivel_academico=%s,
    anio_residencia=%s,meses_solicitados=%s, fecha_inicio=%s, fecha_fin=%s,
    observaciones=%s,cdp_evaluadora=%s,aceptada_cdp=%s, observaciones_cdp=%s, 
    pv_aprobacion=%s,fecha_notificacion=%s WHERE id=%s"""

    cursor = mysql.connection.cursor()
    cursor.execute(sql,(usuario, tipo_prorroga, nro_expediente, referente, 
    fecha_envio_cdp,residente_nombre,dni,region_sanitaria,sede,especialidad,nivel,nivel_academico,
    anio_residencia,meses_solicitados, fecha_inicio,
    fecha_fin, observaciones,cdp_evaluadora,aceptada_cdp, observaciones_cdp,
    pv_aprobacion, fecha_notificacion, id))
    mysql.connection.commit()
    cursor.close()
    return redirect('/prorrogas')
    




@app.route('/prorrogas/borrar/<int:id>')
@login_required
def prorrogas_borrar(id):
    connection = mysql.connection
    cursor = connection.cursor()
    cursor.execute("DELETE FROM prorrogas WHERE id=%s", (id,))
    connection.commit()
    cursor.close()
    return redirect('/prorrogas')


@app.route('/prorrogas/pruebas')
@login_required
def vista_pruebas():
    # Solo renderiza el diseño, sin pasarle datos inexistentes
    return render_template('modulos/prorrogas/pruebas.html')

        
import os
if __name__ == '__main__':
    # Lee el puerto que le da Render, si no existe usa el 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) # debug en False para producción
    
    