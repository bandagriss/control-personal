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
        for indiceVerificacion, valorVerificacion in horarios.iteritems():
            if self.marcacion["salida-"+indiceVerificacion] and len(self.diccionario_permiso) > 0: # marca salida con permiso, marca salida turno (no marca regreso)
                if self.diccionario_permiso["desde"] > valorVerificacion["entrada"] and self.diccionario_permiso["desde"] < valorVerificacion["salida"]:
                    self.diccionario_permiso["hasta"] = valorVerificacion["salida"]
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}

                        
        # ---------------     verificando si olvido marcar  -----------------------------
        # verificar esta parte para los casos en que el usuario llega tarde y no marca salida good!!!
        # verificar para que cuando llega temprano y no marca salida solo le de un permiso desde la hora de entrada valida

        
        #guardando permisos
        permisos_encontrados = self.marcacion["permisos"]
        falto_marcado = {}
        falto_marcado["permisos"] = []
        
        for index, value in horarios.iteritems():
                
            if not self.marcacion["salida-"+index] and len(self.diccionario_permiso) > 0: # tiene permiso y no marco salida
                self.diccionario_permiso["hasta"] = value["salida"]
                self.marcacion["permisos"].append(self.diccionario_permiso)
                self.diccionario_permiso = {}
                print "no marco salida", self.diccionario_permiso
                
            elif self.marcacion["entrada-"+index] and not self.marcacion["salida-"+index] and len(self.diccionario_permiso) == 0: # llego temprano pero se olvido marcar salida
                self.diccionario_permiso["desde"] = value["entrada"]
                self.diccionario_permiso["hasta"] = value["salida"]
                self.marcacion["permisos"].append(self.diccionario_permiso)
                self.diccionario_permiso = {}
                
            elif not self.marcacion["entrada-"+index] and not self.marcacion["salida-"+index]: #no tiene entrada ni salida
                if len(self.marcacion["permisos"]) > 0:
                    for tiene_permiso in permisos_encontrados:
                        for campo, permiso_registrado in tiene_permiso.iteritems():
                            if campo == "hasta":
                                if permiso_registrado > horarios[index]["entrada"] and permiso_registrado < horarios[index]["salida"]:
                                    self.diccionario_permiso["desde"] = permiso_registrado
                                    self.diccionario_permiso["hasta"] = value["salida"]
                                    self.marcacion["permisos"].append(self.diccionario_permiso)
                                    self.diccionario_permiso = {}
                                    
                else:
                    self.diccionario_permiso["desde"] = value["entrada"]
                    self.diccionario_permiso["hasta"] = value["salida"]
                    falto_marcado["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}

            elif not self.marcacion["entrada-"+index] and self.marcacion["salida-"+index] and len(self.marcacion["permisos"]) == 0: # no tiene entrada pero si salida
                # if len(self.marcacion["permisos"]) > 0:
                #     for tiene_permiso in permisos_encontrados:
                #         for campo, permiso_registrado in tiene_permiso.iteritems():
                #             if campo == "hasta":
                #                 if permiso_registrado > horarios[index]["entrada"] and permiso_registrado < horarios[index]["salida"]:
                #                     print permiso_registrado
                                    
                # else:
                self.diccionario_permiso["desde"] = value["entrada"]
                self.diccionario_permiso["hasta"] = value["salida"]
                falto_marcado["permisos"].append(self.diccionario_permiso)
                self.diccionario_permiso = {}

                    
            
                    

        if len(falto_marcado["permisos"]) > 0:
            for noMarcado in falto_marcado["permisos"]:
                self.marcacion["permisos"].append(noMarcado)
                    
        json_marcado["marcado"].append(self.marcacion)
                    
                
                
        #print json.dumps(json_marcado, sort_keys=True, indent=4)
        return json_marcado
            
            



#ejemplo de horas
#horas =["14:30:00","16:30:00", "19:00:00"]
#marcado = Marcado()
#marcado.main(horas)
