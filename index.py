from  flask import Flask, jsonify, render_template, request, redirect,url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import decimal
import mysql.connector
from decimal import Decimal
from datetime import date, datetime

#conexion a la base de datos
app= Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='bdd_banco'
mysql=MySQL(app)

#Home/inicio de sesion
@app.route('/')
def home():
   

    return render_template('home.html')

#Inicio aqui debe validar la cuenta y la contraseña en la base, recibe los parametros de home
#Tiene 3 botones que redirecciona a otras paginas
@app.route('/Inicio', methods=['POST'])
def Inicio():
    
  
    if request.method == 'POST':
        cuenta=request.form['cuenta']
        contrasena=request.form['contrasena']
        cur = mysql.connection.cursor()#cursor a la base de datos obtuene los datos de la cuenta ingresada
        cur.execute('select nombre, cuentaid,saldo from cliente, cuenta where cliente.clienteid=cuenta.clienteid and cuentaid = %s LIMIT 1', cuenta)
        resultados=cur.fetchone()
        #si wxisten resultados los datos consultados los manda a Inicio para que se muestren
        if resultados:
           datos=resultados
           print(datos)
           return render_template('inicio.html', dat=datos) #llama a inicio y muestra los datos de la consulta
        else:
           return'La variable cuenta no se encuentra en la base de datos.'
           
@app.route('/Salir', methods=['POST'])
def Salir(): #boton salir redirecciona al inicio de sesion
    return redirect(url_for('home'))

@app.route('/Historial', methods=['POST'])
def Historial():#boton historial
        datos=request.form['dat']
        c=datos
        curs = mysql.connection.cursor()
        #recupera los datos de la tabla transacciones relacionados a la cuenta con la que inicio sesion
        curs.execute('select transaccionid, cuentaid, tipotransaccion, monto, fechatransaccion from transaccion where cuentaid =%s', c )
        hist=curs.fetchall()
        print(hist)
        return render_template('Historial.html', hs=hist)#manda los datos a una nueva pagina donde los muestra

@app.route('/TransferenciaMenu', methods=['POST'])
def TransferenciaMenu():#boton de transferencia redirige a un menu para pedir los datos de ls tranferencia
        datos=request.form['dat']
        c=datos
        return render_template('TransferenciaMenu.html',dat=c) 

@app.route('/TransferenciaCom', methods=['POST'])
def TransferenciaCom():
        #Hace el commit de la tranferencia
        cuenta=request.form['dat']
        cuentaDestino=request.form['CuentaDestino']
        Monto=request.form['Monto']
        Concepto=request.form['Concepto']
        c=cuenta
        curs = mysql.connection.cursor()
        curs.execute('select saldo from cuenta where cuentaid =%s', c )
        saldo=curs.fetchone()
        valor = Decimal(Monto).quantize(Decimal('000000000.00'))
        fecha=datetime.now()
        print(saldo[0])
        print(valor)
        print(Monto)
        if cuenta == cuentaDestino:
           return 'Error la cuenta es la misma'
        elif saldo[0]>=valor:
               try:
                    curst = mysql.connection.cursor()

                    # Iniciar una transacción
                    # registra la transaccion en la base
                    curst.execute("INSERT INTO transaccion (cuentaid, tipotransaccion, monto, fechatransaccion ) VALUES (%s,%s,%s,%s)",(cuentaDestino,Concepto,valor,fecha))
                    curst.execute("UPDATE cuenta SET Saldo = Saldo - %s WHERE cuentaid =%s", (Monto,cuenta))
                    curst.execute("UPDATE cuenta SET Saldo = Saldo + %s WHERE cuentaid =%s", (Monto,cuentaDestino))
                    mysql.connection.commit()
                    return 'Transaccion exitosa'
               except Exception as e:
                    # Manejar errores
                   return 'error'
        else:
           return 'Monto invalido'


if __name__=='__main__':
    app.run(debug=True)