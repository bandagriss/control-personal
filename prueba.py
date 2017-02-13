#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import pandas as pd
import numpy as np
import requests
from getpass import getpass


from marcado_v2 import Marcado

cabecera1 = {'x-access-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c3VhcmlvIjoiYWRtaW4iLCJpYXQiOjE0ODYzOTU4NjF9.6hukWA93LoY0bsfnuxt_hVWoNGfav6Ury88jozhN2ew'}
url = "http://192.168.27.205:5000/api/v1/registros_rango?inicio=2016-09-01&fin=2016-09-31"
solicitud = requests.get(url, headers = cabecera1)

contador = 1
# recuperamos los datos del servicio en formato json
data = solicitud.json()

#marcado del dia usuario: usuario, fecha: dia que quieres saber
def marcadoDia(usuario, fecha):
    horas = []
    for valor in data:
        if valor["uid"] == usuario and valor["fecha"] == fecha:
            horas.append(valor["hora"])
    return horas

#horas =  marcadoDia("jarteaga", "2016-09-31")

#provando con marcacion dia
#horas =["14:30:00","16:30:00", "19:00:00"]

#marcado = Marcado()
#print marcado.main(horas)
#print "horas que a marcado jarteaga: ", horas


columnas = [
    "uid",
    "hora",
    "dispositivo",
    "fecha"
]

#probando con marcacion fechas
def marcadoFecha(usuario):
    datos = pd.DataFrame(data, columns=columnas)
    #return datos.head()
    #return datos[datos['uid'] == 'jarteaga']
    #return datos[(datos['uid'] == usuario) & (datos['fecha'] == '2016-09-30')]
    return datos.groupby(["uid", "fecha"])["hora"].count()
#horas = marcadoFecha("jarteaga")
#print horas

def usuarioFechas():
    horas_registradas = []
    datos = pd.DataFrame(data, columns=columnas)
    for name, group in datos[datos["uid"] == "jarteaga"].groupby(["fecha", "uid"]):
        horas =  group["hora"]
        for hora in horas:
            horas_registradas.append(hora)
        marcado = Marcado()
        resultado =  marcado.main(horas_registradas)
        print json.dumps(resultado, sort_keys=True, indent=4)
        horas_registradas = []

# def test_with_setup(benchmark):
#     benchmark.pedantic(something, setup=usuarioFechas, args=(1, 2, 3), kwargs={'foo': 'bar'}, iterations=10, rounds=100)

#funciona para saber cuanto tardo la ejecucion del script
def test():
    usuarioFechas()

if __name__ == '__main__':
    import timeit
    t = timeit.timeit("test()",setup="from __main__ import test", number=1)
    print "tiempo de ejecucion : ", t




    



    


    




#marcado = Marcado()
#print marcado.main(horas)
#print "horas que a marcado jarteaga: ", horas
