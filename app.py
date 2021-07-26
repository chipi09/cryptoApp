from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from http import HTTPStatus
import dataaccess
import requests
import sqlite3

app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app)
dbManager = dataaccess.DBmanager(app.root_path + app.config.get('DATABASE'))
criptos = ['BTC','ETH','XRP','LTC','BCH','BNB','USDT','EOS','BSV','XLM','ADA','TRX']

@app.route("/")
def spa():
    return render_template("spa.html")

@app.route("/api/v1/movimientos", methods=['GET'])
def movimientos():
    try:
        query = "SELECT id, date, time, moneda_from, round(cantidad_from, 4) , moneda_to, round(cantidad_to, 4) FROM movimientos ORDER BY id;"
        lista = dbManager.consulta(query)
        json = {
            "status" : "success",
            "data" : lista
        }
        return jsonify(json), HTTPStatus.OK
    except sqlite3.Error as e:
        return jsonify({"status": "fail", "mensaje": "Error en base de datos: {}".format(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({"status": "fail", "mensaje": "Error en el controlador /api/v1/movimientos : {}".format(e)}), HTTPStatus.BAD_REQUEST         

@app.route("/api/v1/status", methods=['GET'])
def status():
    try:
        query = "SELECT cantidad_from FROM movimientos WHERE moneda_from = 'EUR' ORDER BY id  ;"
        lista = dbManager.consulta(query)
        lista = [i[0] for i in lista]
        euros_invertidos = sum(lista)

        query = "SELECT cantidad_to FROM movimientos WHERE moneda_to = 'EUR' ORDER BY id  ;"
        lista = dbManager.consulta(query)
        lista = [i[0] for i in lista]
        euros_devueltos = sum(lista)

        saldo_euros_invertidos = euros_devueltos - euros_invertidos

        valor_cripto_euros = 0
        valor_criptos_euros = list()

        for cripto in criptos:
            valor_cripto_from = getAllCantidadByMoneda(cripto, "from")
            if (valor_cripto_from > 0):
                url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?symbol=' + cripto + '&amount=' + str(valor_cripto_from) + '&convert=' + 'EUR' + '&CMC_PRO_API_KEY=' + app.config.get('API_KEY')
                response = requests.get(url)
                json = response.json()
                valor_cripto_from_euros = json['data']['quote']['EUR']['price']
            else:
                valor_cripto_from_euros = 0

            valor_cripto_to = getAllCantidadByMoneda(cripto, "to")
            if (valor_cripto_to > 0):
                url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?symbol=' + cripto + '&amount=' + str(valor_cripto_to) + '&convert=' + 'EUR' + '&CMC_PRO_API_KEY=' + app.config.get('API_KEY')
                response = requests.get(url)
                json = response.json()
                valor_cripto_to_euros = json['data']['quote']['EUR']['price']
            else:
                valor_cripto_to_euros = 0

            valor_cripto_euros = valor_cripto_to_euros - valor_cripto_from_euros
            valor_criptos_euros.append(valor_cripto_euros)

        valor_euros_criptos_total = sum(valor_criptos_euros)
        valor_actual = euros_invertidos + saldo_euros_invertidos + valor_euros_criptos_total
        json = {
            "status" : "success",
            "data" : {
                "invertido" : euros_invertidos,
                "valor_actual" : round(valor_actual, 2)
            }
        }
        return jsonify(json), HTTPStatus.OK
    except Exception as e:
        return jsonify({"status": "fail", "mensaje": "Error en el controlador /api/v1/status : {}".format(e)}), HTTPStatus.BAD_REQUEST  

@app.route("/api/v1/movimiento/<int:id>", methods=['GET'])
@app.route("/api/v1/movimiento", methods=['POST'])
def movimiento(id=None):
    try:
        if request.method == 'POST':
            json = request.get_json()
            fecha = json['fecha']
            hora = json['hora']
            from_moneda = json['from_moneda']
            from_cantidad = json['from_cantidad']
            to_moneda = json['to_moneda']
            to_cantidad = json['to_cantidad']
            if (not fecha or not hora or not from_moneda or not from_cantidad or not to_moneda or not to_cantidad):
                return jsonify({"status": "fail", "mensaje": "Error en el controlador /api/v1/movimiento: campo json vacio"}), HTTPStatus.BAD_REQUEST
            if (from_moneda == to_moneda):
                return jsonify({"status": "fail", "mensaje": "Error en el controlador /api/v1/movimiento: misma moneda"}), HTTPStatus.BAD_REQUEST
            if (from_moneda != 'EUR'):
                cantidad_to = getAllCantidadByMoneda(from_moneda, 'to')
                cantidad_from = getAllCantidadByMoneda(from_moneda, 'from')
                saldo = cantidad_to - cantidad_from
                if (saldo < float(from_cantidad)):
                    return jsonify({"status": "fail", "mensaje": "saldo insuficiente"}), HTTPStatus.OK

            query = "INSERT INTO movimientos (date, time, moneda_from, cantidad_from, moneda_to, cantidad_to) values (" + "'" + fecha + "','" + hora + "','" + from_moneda + "'," +  from_cantidad + ",'" + to_moneda + "'," + to_cantidad + ") ;"
            id = dbManager.insert(query)

            json = {
                "status" : "success",
                "id" : id,
                "monedas" : [from_moneda, to_moneda]
            }
            return jsonify(json), HTTPStatus.CREATED

        if request.method == 'GET':
            query = "SELECT * FROM movimientos WHERE id=" + id + " ;"
            lista = dbManager.consulta(query)

            json = {
                "status" : "success",
                "data" : lista
            }
            return jsonify(json), HTTPStatus.ACCEPTED

    except sqlite3.Error as e:
        return jsonify({"status": "fail", "mensaje": "Error en base de datos: {}".format(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({"status": "fail", "mensaje": "Error en el controlador /api/v1/movimiento: {}".format(e)}), HTTPStatus.BAD_REQUEST


@app.route("/api/v1/convertir-moneda", methods=['POST'])
def convertirMoneda():
    try:
        json = request.get_json()
        from_moneda = json['from_moneda']
        to_moneda = json['to_moneda']
        from_cantidad = json['from_cantidad']
        if (not from_moneda or not from_cantidad or not to_moneda):
            return jsonify({"status": "fail", "mensaje": "Error en el controlador /api/v1/convertir-moneda: campo json vacio"}), HTTPStatus.BAD_REQUEST
        url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?symbol=' + from_moneda + '&amount=' + str(from_cantidad) + '&convert=' + to_moneda + '&CMC_PRO_API_KEY=' + app.config.get('API_KEY')
        response = requests.get(url)
        json = response.json()

        to_cantidad = json['data']['quote'][to_moneda]['price']
        return jsonify({"to_cantidad": to_cantidad}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"status": "fail", "mensaje": "Error en el controlador /api/v1/convertir-moneda: {}".format(e)}), HTTPStatus.BAD_REQUEST

@app.route("/api/v1/comprobar-saldo/<moneda>/<cantidad>", methods=['GET'])
def comprobarSaldo(moneda, cantidad):
    try:
        cantidad_to = getAllCantidadByMoneda(moneda, "to")
        cantidad_from = getAllCantidadByMoneda(moneda, "from")
        saldo = cantidad_to - cantidad_from
        if (saldo < float(cantidad)):
            return jsonify({"status": "fail", "mensaje": "saldo insuficiente"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"status": "fail", "mensaje": "Error en el controlador /api/v1/comprobar-saldo/<moneda>/<cantidad>: {}".format(e)}), HTTPStatus.BAD_REQUEST            

def getAllCantidadByMoneda(moneda, switch):
    query = "SELECT cantidad_" + switch + " FROM movimientos WHERE moneda_" + switch + " = '" + moneda + "'  ;"
    lista = dbManager.consulta(query)
    lista = [i[0] for i in lista]
    return sum(lista)

@app.route("/api/v1/actualizar-api", methods=['GET'])
def actualizarApi():
    url = "https://pro-api.coinmarketcap.com/v1/key/info?CMC_PRO_API_KEY=" + app.config.get('API_KEY')
    response = requests.get(url)
    json = response.json()
    limite_diario = json['data']['plan']['credit_limit_daily']
    limite_mensual = json['data']['plan']['credit_limit_monthly']
    usos_dia_actual = json['data']['usage']['current_day']['credits_used']
    usos_mes_actual = json['data']['usage']['current_month']['credits_used']
    respuesta = {
        "limite_diario" : limite_diario,
        "limite_mensual" : limite_mensual,
        "usos_dia_actual" : usos_dia_actual,
        "usos_mes_actual" : usos_mes_actual
    }
    return jsonify(respuesta), HTTPStatus.OK            