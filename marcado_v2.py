#!/usr/bin/env python
# -*- coding: utf-8
import json
import sys
from datetime import datetime

class Marcado():
    def __init__(self):
        self.diccionario_permiso = {}
        self.tiempos = {}


    def horarioContinuo(self):
        self.marcacion = {
            "entrada-horario-continuo":{},
            "salida-horario-continuo": {},            
            "permisos": [],
        }

    def horarioNormalDosTurnos(self):
        self.marcacion = {
            "entrada-manana":{},
            "salida-manana": {},            
            "entrada-tarde":{},
            "salida-tarde": {},            
            "permisos": [],
        }

    def horarioNormalTresTurnos(self):
        self.marcacion = {
            "entrada-manana":{},
            "salida-manana": {},            
            "entrada-tarde":{},
            "salida-tarde": {},
            "entrada-noche": {},
            "salida-noche": {},
            "permisos": [],
        }
        

    def convertir_fecha(self, hora):
        return datetime.strptime(hora, "%H:%M:%S")

    def marcado(self, hora, horarios, json_marcado, permiso, contador):
        fecha = self.convertir_fecha(hora)
        for indice, valor in horarios.iteritems():
            if self.convertir_fecha(valor["min_entrada"]) <= fecha and fecha <= self.convertir_fecha(valor["entrada"]):
                self.marcacion["entrada-"+indice] = hora

            elif fecha > self.convertir_fecha(valor["entrada"]) and fecha < self.convertir_fecha(valor["salida"]): #esta llegando atrasado o esta saliendo y entrando, entonces generamos permisos
                if permiso == "entrada" and contador == 1: # esta llegando despues de la hora de entrada y es la primera vez , por eso puede ser atraso o permiso
                    self.diccionario_permiso["desde"] = valor["entrada"]
                    self.diccionario_permiso["hasta"] = hora
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}
                if permiso == "entrada" and contador > 1: # esta llegando de algun permiso
                    self.diccionario_permiso["hasta"] = hora
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}
                if permiso == "salida": # es una salida que esta realizando el sujeto ya que esta en horario de trabajo y marco
                    self.diccionario_permiso["desde"] = hora
            elif fecha >= self.convertir_fecha(valor["salida"]) and fecha <= self.convertir_fecha(valor["max_salida"]): # esta saliendo de la oficina
                self.marcacion["salida-"+indice] = hora
            


    def marcadoTurno(self, horarios, horas, turno):
        horas_registradas = []
        for hora in horas:
            if hora > horarios[turno]["min_entrada"] and hora < horarios[turno]["max_salida"]:
                horas_registradas.append(hora)
        return horas_registradas

    def verificacionEntrada(self, horarios):
        marcacion_auxiliar = {}
        marcacion_auxiliar["permisos"] = []
        #verificamos que no haya vuelto de alguna salida
        for index, value in horarios.iteritems():
            if len(self.diccionario_permiso) > 0:
                if self.diccionario_permiso["desde"] > value["entrada"] and self.diccionario_permiso["desde"] < value["salida"]: # salio y no marco entrada entonces se genera un permiso hasta el final del dia
                    self.diccionario_permiso["hasta"]  = value["salida"]
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}
                    
                    if not self.marcacion["entrada-"+index] and not self.marcacion["salida-"+index]:
                        if  len(self.marcacion["permisos"]) > 0:
                            for permisos in self.marcacion["permisos"]:
                                u = 1
                        else:
                            self.diccionario_permiso["desde"] = value["entrada"]
                            self.diccionario_permiso["hasta"]  = value["salida"]
                            self.marcacion["permisos"].append(self.diccionario_permiso)
                            self.diccionario_permiso = {}
        #volvemos a iterar para buscar faltas en la tarde y en la mañana
        for indice, valor in horarios.iteritems():
            if not self.marcacion["salida-"+indice]:
                if len(self.marcacion["permisos"]) > 0 and not self.marcacion["salida-"+indice]:
                    for permisos in self.marcacion["permisos"]:
                        for campo, permiso_hora in permisos.iteritems():
                            if campo == "hasta":
                                if permiso_hora > valor["entrada"] and permiso_hora < valor["salida"]:
                                    print "la hora maxima del permiso es :" , permiso_hora
                                    #revisar esto esta medio loco pero vamos
                                    self.diccionario_permiso["desde"] = permiso_hora
                                    self.diccionario_permiso["hasta"]  = valor["salida"]
                                    marcacion_auxiliar["permisos"].append(self.diccionario_permiso)
                                    self.diccionario_permiso = {}
                                else:
                                #if permiso_hora >= valor["salida"] and permiso_hora < valor["entrada"]:
                                    if permiso_hora != valor["salida"]:
                                        self.diccionario_permiso["desde"] = valor["entrada"]
                                        self.diccionario_permiso["hasta"]  = valor["salida"]
                                        marcacion_auxiliar["permisos"].append(self.diccionario_permiso)
                                        self.diccionario_permiso = {}
                                
                else:
                    self.diccionario_permiso["desde"] = valor["entrada"]
                    self.diccionario_permiso["hasta"]  = valor["salida"]
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}
                    
            #no marco entrada y solo marco salida        
            if not self.marcacion["entrada-"+indice] and self.marcacion["salida-"+indice] and len(self.marcacion["permisos"]) == 0:
                self.diccionario_permiso["desde"] = valor["entrada"]
                self.diccionario_permiso["hasta"]  = valor["salida"]
                marcacion_auxiliar["permisos"].append(self.diccionario_permiso)
                self.diccionario_permiso = {}

                
        #recuperando             
        for auxiliar in marcacion_auxiliar["permisos"]:
            self.marcacion["permisos"].append(auxiliar)
        

    #principal
    def main(self, horas, uid, fecha, dispositivo, Turnos):
        if Turnos == "UNO":
            horarios = {
                "horario-continuo":{
                    "min_entrada": "05:00:00",
                    "entrada": "08:40:00",
                    "salida": "16:00:00",
                    "max_salida": "23:59:59",
                }
            }
            horasM = self.marcadoTurno(horarios, horas, "horario-continuo")
            self.horarioContinuo()

        elif Turnos == "DOS":
            horarios = {
                "manana":{
                    "min_entrada": "05:00:00",
                    "entrada": "08:40:00",
                    "salida": "12:00:00",
                    "max_salida": "13:30:00",
                },
                "tarde":{
                    "min_entrada": "13:30:00",
                    "entrada": "14:30:00",
                    "salida": "19:00:00",
                    "max_salida": "23:59:59",
                }
            }

            horasM = self.marcadoTurno(horarios, horas, "manana")
            horasT = self.marcadoTurno(horarios, horas, "tarde")
            self.horarioNormalDosTurnos()
                 
        elif Turnos =="TRES":
            horarios = {
                "manana":{
                    "min_entrada": "05:00:00",
                    "entrada": "08:40:00",
                    "salida": "12:00:00",
                    "max_salida": "13:30:00",
                },
                "tarde":{
                    "min_entrada": "13:30:00",
                    "entrada": "14:30:00",
                    "salida": "17:00:00",
                    "max_salida": "17:59:59",
                },
                "noche":{
                    "min_entrada": "18:00:00",
                    "entrada": "18:30:00",
                    "salida": "22:30:00",
                    "max_salida": "23:59:59",
                }
            }

            horasM = self.marcadoTurno(horarios, horas, "manana")
            horasT = self.marcadoTurno(horarios, horas, "tarde")
            horasN = self.marcadoTurno(horarios, horas, "noche")
            self.horarioNormalTresTurnos()
            

        
        
        json_marcado = {
            "marcado":[],
        }

        #llena de datos basicos uid, fecha, dispositivo
        json_marcado["uid"] = uid
        json_marcado["fecha"] = fecha
        json_marcado["dispositivo"] = dispositivo
        
        
        if Turnos == "UNO":
            #horario continuo
            count = 1
            if len(horasM) > 0:
                for hora in horasM:
                    if count%2 == 0:
                        self.marcado(hora, horarios, json_marcado, "salida", count)
                        count+=1
                    else:
                        self.marcado(hora, horarios, json_marcado, "entrada", count)
                        count+=1
        if Turnos == "DOS":
            #manana
            count = 1
            if len(horasM) > 0:
                for hora in horasM:
                    if count%2 == 0:
                        self.marcado(hora, horarios, json_marcado, "salida", count)
                        count+=1
                    else:
                        self.marcado(hora, horarios, json_marcado, "entrada", count)
                        count+=1
            #tarde    
            count = 1
            if len(horasT) > 0:
                for hora in horasT:
                    if count%2 == 0:
                        self.marcado(hora, horarios, json_marcado, "salida", count)
                        count+=1
                    else:
                        self.marcado(hora, horarios, json_marcado, "entrada", count)
                        count+=1
                        
        if Turnos == "TRES":
            #manana
            count = 1
            if len(horasM) > 0:
                for hora in horasM:
                    if count%2 == 0:
                        self.marcado(hora, horarios, json_marcado, "salida", count)
                        count+=1
                    else:
                        self.marcado(hora, horarios, json_marcado, "entrada", count)
                        count+=1
            #tarde    
            count = 1
            if len(horasT) > 0:
                for hora in horasT:
                    if count%2 == 0:
                        self.marcado(hora, horarios, json_marcado, "salida", count)
                        count+=1
                    else:
                        self.marcado(hora, horarios, json_marcado, "entrada", count)
                        count+=1
            #noche
            count = 1
            if len(horasN) > 0:
                for hora in horasN:
                    if count%2 == 0:
                        self.marcado(hora, horarios, json_marcado, "salida", count)
                        count+=1
                    else:
                        self.marcado(hora, horarios, json_marcado, "entrada", count)
                        count+=1


        #verificando que  exista una salida sin regreso
        
        self.verificacionEntrada(horarios)
        ## fin verificacion

        json_marcado["marcado"].append(self.marcacion)
                    

                    
                
                
        #print json.dumps(json_marcado, sort_keys=True, indent=4)
        return json_marcado
            
            



#ejemplo de horas
#horas =["14:30:00","16:30:00", "19:00:00"]
#marcado = Marcado()
#marcado.main(horas)
