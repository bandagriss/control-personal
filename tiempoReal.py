#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import time

#clases locales
from marcado_v2 import Marcado

class TiempoReal(object):
    
    def __init__(self):
        print "marcando en tiempo real"

    
    def marcacion_real(self, horas_registradas, uid, fecha, dispositivo):  #horas_registradas es un array de horas, uid=usuario, fecha, dispositivo
        marcado = Marcado()
        resultado = marcado.main(horas_registradas,uid, fecha, dispositivo, "DOS")
        print chr(27)+"[1;32m"+ "Mostrando servicio para reportes" + chr(27)+"[0m"
        print(json.dumps(resultado, sort_keys=False, indent=4)+ ",")
        marcacion_dia = {
            "marcado" : [],
        }
        horas_encontradas = {}
        permisos_encontrados = {
            "permisos": [],
        }
        print chr(27)+"[1;32m"+ "Mostrando en tiempo real" + chr(27)+"[0m"
        for res, value in resultado.iteritems():
            marcacion_dia["uid"] = uid
            marcacion_dia["fecha"] = fecha
            marcacion_dia["dispositivo"] = dispositivo
            if res == "marcado":
                for marcaciones_registrada in value:
                    for tipo, hora_marcado in marcaciones_registrada.iteritems():
                        if tipo == "entrada-manana":
                            permisos_encontrados["entrada-manana"] = hora_marcado
                        if tipo == "salida-manana":
                            permisos_encontrados["salida-manana"] = hora_marcado
                        if tipo == "entrada-tarde":
                            permisos_encontrados["entrada-tarde"] = hora_marcado
                        if tipo == "salida-tarde":
                            permisos_encontrados["salida-tarde"] = hora_marcado
                        if tipo == "permisos":
                            if len(hora_marcado) > 0:
                                #for campo, permiso in hora_marcado.iteritems():
                                for permisos in hora_marcado: # entramos a los permisos hasta desde
                                    for campo, permiso in permisos.iteritems():
                                        if campo == "hasta":
                                            #if permiso < time.strftime("%H:%M:%S"):
                                            hora_ejemplo = "15:10:00"
                                            if permiso < hora_ejemplo:
                                                horas_encontradas["hasta"] = permiso
                                                #horas_encontradas["desde"] = permisos["desde"]
                                        if campo == "desde":
                                            #else:
                                            if permiso < hora_ejemplo:
                                                horas_encontradas["desde"] = permisos["desde"]
                                            
                                    if len(horas_encontradas) > 0:
                                        permisos_encontrados["permisos"].append(horas_encontradas)
                                        horas_encontradas = {}
                            else:
                                print "no tiene permisos"
        marcacion_dia["marcado"].append(permisos_encontrados)
        print json.dumps(marcacion_dia, sort_keys=True, indent=4)
                
        

if __name__ == '__main__':
    horas_registradas = ["08:25:00","09:00:00"]
    #horas_registradas = ["08:45:00", "12:15:00", "14:15:00"]
    
    uid = "jarteaga"
    fecha = "2017-02-09"
    dispositivo = "OF1IZQ"
    real = TiempoReal()
    real.marcacion_real(horas_registradas, uid, fecha, dispositivo)

    


        
        
