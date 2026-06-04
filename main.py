from flask import Flask, render_template, request,redirect  # <--- Asegúrate de agregar , render_template aquí
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
import MySQLdb.cursors 


app = Flask(__name__)

mysql=MySQL()

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_PORT']= 3306
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='residencias'
mysql.init_app(app)
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


@app.route('/')
def index():
    # Esto le dice a Flask que vaya a buscar el archivo index.html dentro de 'templates'
    return render_template('index.html') 


@app.route('/reevaluaciones')  # <-- Agregamos la ruta que faltaba
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
def reevaluaciones_guardar():
    # Tu código actual se queda EXACTAMENTE IGUAL. 
    # request.form['referente'] y request.form['especialidad'] 
    # van a atrapar de forma automática la opción que el usuario haya elegido en el select.
    usuario                 = request.form['usuario']
    tipo_de_reevaluacion    = request.form['tipo_de_reevaluacion']
    expediente              = request.form['expediente']
    referente               = request.form['referente']
    fecha_envio_cdp         = request.form['fecha_envio_cdp']
    apellido_nombre_residente = request.form['apellido_nombre_residente']
    dni                     = request.form['dni']
    region_sanitaria        = request.form['region_sanitaria']
    sede_de_residencia      = request.form['sede_de_residencia']
    especialidad            = request.form['especialidad']
    nivel                   = request.form['nivel']
    ano_residencia          = request.form['ano_residencia']
    sede_reevaluacion       = request.form['sede_reevaluacion']
    tiempo_solicitado_reevaluacion_meses = request.form['tiempo_solicitado_reevaluacion_meses']
    fecha_inicio_reevaluacion = request.form['fecha_inicio_reevaluacion']
    fecha_finalizacion_reevaluacion = request.form['fecha_finalizacion_reevaluacion']
    incluye_extension_peri_de_residencia = request.form['incluye_extension_peri_de_residencia']
    nombre_cdp_evaluador    = request.form['nombre_cdp_evaluador']
    aceptada_por_cdp        = request.form['aceptada_por_cdp']
    observaciones_cdp       = request.form['observaciones_cdp']
    disposicion_de_aprobacion = request.form['disposicion_de_aprobacion']
    resultado_reevaluacion  = request.form['resultado_reevaluacion']
    observaciones           = request.form['observaciones']

    sql = """INSERT INTO reevaluaciones (
    usuario, tipo_de_reevaluacion, expediente, referente, 
    fecha_envio_cdp, apellido_nombre_residente, dni, region_sanitaria, 
    sede_de_residencia, especialidad, nivel, ano_residencia, 
    sede_reevaluacion, tiempo_solicitado_reevaluacion_meses, fecha_inicio_reevaluacion, 
    fecha_finalizacion_reevaluacion, incluye_extension_peri_de_residencia, nombre_cdp_evaluador, 
    aceptada_por_cdp, observaciones_cdp, disposicion_de_aprobacion, resultado_reevaluacion, 
    observaciones
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    connection = mysql.connection
    cursor = connection.cursor()
    cursor.execute(sql, (usuario, tipo_de_reevaluacion, expediente, referente, 
    fecha_envio_cdp, apellido_nombre_residente, dni, region_sanitaria, 
    sede_de_residencia, especialidad, nivel, ano_residencia, 
    sede_reevaluacion, tiempo_solicitado_reevaluacion_meses, fecha_inicio_reevaluacion, 
    fecha_finalizacion_reevaluacion, incluye_extension_peri_de_residencia, nombre_cdp_evaluador, 
    aceptada_por_cdp, observaciones_cdp, disposicion_de_aprobacion, resultado_reevaluacion, 
    observaciones))
    mysql.connection.commit()
    cursor.close()
    return redirect('/reevaluaciones')

@app.route('/modulos/reevaluaciones/edit/<int:id>')
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
        sede_de_residencia = request.form['sede_de_residencia']
        especialidad = request.form['especialidad']
        nivel = request.form['nivel']
        ano_residencia = request.form['ano_residencia']
        sede_reevaluacion = request.form['sede_reevaluacion']
        tiempo_solicitado_reevaluacion_meses = request.form['tiempo_solicitado_reevaluacion_meses']
        fecha_inicio_reevaluacion = request.form['fecha_inicio_reevaluacion']
        fecha_finalizacion_reevaluacion = request.form['fecha_finalizacion_reevaluacion']
        incluye_extension_peri_de_residencia = request.form['incluye_extension_peri_de_residencia']
        nombre_cdp_evaluador = request.form['nombre_cdp_evaluador']
        aceptada_por_cdp = request.form['aceptada_por_cdp']
        observaciones_cdp = request.form['observaciones_cdp']
        disposicion_de_aprobacion = request.form['disposicion_de_aprobacion']
        resultado_reevaluacion = request.form['resultado_reevaluacion']
        observaciones = request.form['observaciones']

        # La orden SQL con SET para modificar los campos existentes
        sql = """UPDATE reevaluaciones SET 
            usuario=%s, tipo_de_reevaluacion=%s, expediente=%s, referente=%s, 
            fecha_envio_cdp=%s, apellido_nombre_residente=%s, dni=%s, region_sanitaria=%s, 
            sede_de_residencia=%s, especialidad=%s, nivel=%s, ano_residencia=%s, 
            sede_reevaluacion=%s, tiempo_solicitado_reevaluacion_meses=%s, fecha_inicio_reevaluacion=%s, 
            fecha_finalizacion_reevaluacion=%s, incluye_extension_peri_de_residencia=%s, nombre_cdp_evaluador=%s, 
            aceptada_por_cdp=%s, observaciones_cdp=%s, disposicion_de_aprobacion=%s, resultado_reevaluacion=%s, 
            observaciones=%s 
            WHERE id=%s"""

        cursor = mysql.connection.cursor()
        # Pasamos las 23 variables + el ID al final (en total 24 elementos)
        cursor.execute(sql, (
            usuario, tipo_de_reevaluacion, expediente, referente, 
            fecha_envio_cdp, apellido_nombre_residente, dni, region_sanitaria, 
            sede_de_residencia, especialidad, nivel, ano_residencia, 
            sede_reevaluacion, tiempo_solicitado_reevaluacion_meses, fecha_inicio_reevaluacion, 
            fecha_finalizacion_reevaluacion, incluye_extension_peri_de_residencia, nombre_cdp_evaluador, 
            aceptada_por_cdp, observaciones_cdp, disposicion_de_aprobacion, resultado_reevaluacion, 
            observaciones, id
        ))
        mysql.connection.commit()
        cursor.close()
        return redirect('/reevaluaciones')
    


@app.route('/reevaluaciones/borrar/<int:id>')
def reevaluaciones_borrar(id):
    connection = mysql.connection
    cursor = connection.cursor()
    cursor.execute("DELETE FROM reevaluaciones WHERE id=%s", (id,))
    connection.commit()
    cursor.close()
    return redirect('/reevaluaciones')



@app.route('/prorrogas')
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
    nivel_organizacion      = request.form['nivel_organizacion']
    anio_residencia         = request.form['anio_residencia']
    meses_solicitados       = request.form['meses_solicitados']
    fecha_inicio            = request.form['fecha_inicio']
    fecha_fin               = request.form['fecha_fin']
    observaciones           = request.form['observaciones']
    cdp_evaluadora          = request.form['cdp_evaluadora']
    avalada_cdp             = request.form['avalada_cdp']
    observaciones_cdp       = request.form['observaciones_cdp']
    pv_aprobacion           = request.form['pv_aprobacion']
    fecha_notificacion      = request.form['fecha_notificacion']


    sql= """INSERT INTO prorrogas (usuario, tipo_prorroga, nro_expediente,
    referente,fecha_envio_cdp, residente_nombre, dni, region_sanitaria, 
    sede, especialidad, nivel_organizacion, anio_residencia,meses_solicitados,
    fecha_inicio,fecha_fin,observaciones, cdp_evaluadora, 
    avalada_cdp, observaciones_cdp, pv_aprobacion, fecha_notificacion 
        
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
              %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s, %s)"""
    connection=mysql.connection
    cursor=connection.cursor()
    cursor.execute(sql,( usuario, tipo_prorroga, nro_expediente, referente, 
    fecha_envio_cdp, residente_nombre, dni, region_sanitaria, 
    sede, especialidad, nivel_organizacion, anio_residencia, 
    meses_solicitados, fecha_inicio, fecha_fin,observaciones, cdp_evaluadora, 
    avalada_cdp, observaciones_cdp, pv_aprobacion, fecha_notificacion ))
    mysql.connection.commit()
    cursor.close()
    return redirect('/prorrogas')


@app.route('/modulos/prorrogas/edit/<int:id>')
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
        nivel_organizacion      = request.form['nivel_organizacion']
        anio_residencia         = request.form['anio_residencia']
        meses_solicitados       = request.form['meses_solicitados']
        fecha_inicio            = request.form['fecha_inicio']
        fecha_fin               = request.form['fecha_fin']
        observaciones           = request.form['observaciones']
        cdp_evaluadora          = request.form['cdp_evaluadora']
        avalada_cdp             = request.form['avalada_cdp']
        observaciones_cdp       = request.form['observaciones_cdp']
        pv_aprobacion           = request.form['pv_aprobacion']
        fecha_notificacion      = request.form['fecha_notificacion']


    # La orden SQL con SET para modificar los campos existentes
    sql ="""UPDATE prorrogas SET usuario=%s, tipo_prorroga=%s, nro_expediente=%s, 
    referente=%s, fecha_envio_cdp=%s,residente_nombre=%s, dni=%s, 
    region_sanitaria=%s,sede=%s, especialidad=%s, nivel_organizacion=%s,
    anio_residencia=%s,meses_solicitados=%s, fecha_inicio=%s, fecha_fin=%s,
    observaciones=%s,cdp_evaluadora=%s,avalada_cdp=%s, observaciones_cdp=%s, 
    pv_aprobacion=%s,fecha_notificacion=%s WHERE id=%s"""

    cursor = mysql.connection.cursor()
    cursor.execute(sql,(usuario, tipo_prorroga, nro_expediente, referente, 
    fecha_envio_cdp,residente_nombre,dni,region_sanitaria,sede,
    especialidad,nivel_organizacion, anio_residencia,meses_solicitados, fecha_inicio,
    fecha_fin, observaciones,cdp_evaluadora,avalada_cdp, observaciones_cdp,
    pv_aprobacion, fecha_notificacion, id))
    mysql.connection.commit()
    cursor.close()
    return redirect('/prorrogas')
    




@app.route('/prorrogas/borrar/<int:id>')
def prorrogas_borrar(id):
    connection = mysql.connection
    cursor = connection.cursor()
    cursor.execute("DELETE FROM prorrogas WHERE id=%s", (id,))
    connection.commit()
    cursor.close()
    return redirect('/prorrogas')


@app.route('/prorrogas/pruebas')
def vista_pruebas():
    # Solo renderiza el diseño, sin pasarle datos inexistentes
    return render_template('modulos/prorrogas/pruebas.html')

if __name__ == '__main__':
        app.run(debug=True)  # <-- Fíjate en los 4 espacios de separación con el margen