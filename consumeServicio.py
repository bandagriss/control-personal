#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
import pandas as pd
import requests
import timeit
from getpass import getpass

from prueba import Marcado

cabecera1 = {'x-access-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c3VhcmlvIjoiYWRtaW4iLCJpYXQiOjE0ODYzOTU4NjF9.6hukWA93LoY0bsfnuxt_hVWoNGfav6Ury88jozhN2ew'}
url = "http://192.168.27.205:5000/api/v1/registros_rango?inicio=2016-09-01&fin=2016-09-31"
solicitud = requests.get(url, headers = cabecera1)

# recuperamos los datos del servicio en formato json
data = solicitud.json()

#marcado del dia usuario: usuario, fecha: dia que quieres saber
def marcadoDia(usuario, fecha):
    horas = []
    for valor in data:
        if valor["uid"] == usuario and valor["fecha"] == fecha:
            horas.append(valor["hora"])
    return horas


columnas = [
    "uid",
    "hora",
    "dispositivo",
    "fecha"
]

def usuarioFechas():

    datos = pd.DataFrame(data, columns=columnas)
    #count = 1
    for name, group in datos.groupby(["fecha", "uid"]):
    #for name, group in datos[datos["uid"] == "jarteaga"].groupby(["fecha", "uid"]):
        horas_registradas = []
        horas =  group["hora"]

        uids = group["uid"]
        fechas = group["fecha"]
        dispositivos = group["dispositivo"]
        #sacamos los datos basicos
        for uid in uids:
            uid = uid
            break

        for fecha in fechas:
            fecha = fecha
            break

        for dispositivo in dispositivos:
            dispositivo = dispositivo
            break

        #sacamos las horas de un usuario
        for hora in horas:
            horas_registradas.append(hora)
            
        marcado = Marcado()
        horas_registradas = ["08:55:00", "15:01:00"]  #mandando horas manualmente
        #DATOS "UNO" = Un turno, "DOS" = "Dos turnos"
        print horas_registradas
        resultado =  marcado.main(horas_registradas, uid, fecha, dispositivo, "UNO")
        print(json.dumps(resultado, sort_keys=False, indent=4)+ ",")  #imprime en consola el json


#funciona para saber cuanto tardo la ejecucion del script
def test():
    usuarioFechas()


def imprime(nombre_funcion, repeticion):
    tiempo = []
    for x in range(0,repeticion):
        tiempo.append(timeit.timeit(nombre_funcion, setup="from __main__ import test", number=1))
    minimo =  min(tiempo)
    maximo = max(tiempo)

    contador = 1
    for resultado in tiempo:
        if resultado == minimo:
            print contador, chr(27)+"[1;32m"+ "tiempo de ejecucion minimo ", str(resultado), "seg" + chr(27)+"[0m"
        elif resultado == maximo:
            print contador, chr(27)+"[1;31m"+ "tiempo de ejecucion maximo ", str(resultado), "seg" + chr(27)+"[0m"
        else:
            print contador,  chr(27)+"[1;33m"+ "tiempo de ejecucion normal ", str(resultado), "seg" + chr(27)+"[0m"
        contador+=1
        
    print "minimo: ", minimo
    print "maximo: ", maximo
    print "La diferencia de tiempos entre el max y min es de: ", maximo-minimo, "seg"

def creartxt():
    archi = open('marcado.txt', 'w')
    archi.close()

def grabartxt(json):
    archi=open('marcado.txt', 'a')
    archi.write(json)
    archi.close()


if __name__ == '__main__':
    creartxt()
    imprime("test()", 1)
