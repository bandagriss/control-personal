#!/usr/bin/env python
# -*- coding: utf-8
import json
from datetime import datetime

class Marcado():
    def __init__(self):
        self.diccionario_permiso = {}
        self.marcacion = {
            "entrada-manana":{},
            "entrada-tarde":{},
            "permisos": [],
            "salida-manana": {},
            "salida-tarde": {},
        }
        self.tiempos = {}

    def convertir_fecha(self, hora):
        return datetime.strptime(hora, "%H:%M:%S")

    def aTiempo(self,hora):
        return hora
        
    def marcado(self, hora, horarios, json_marcado, permiso, contador):
        fecha = self.convertir_fecha(hora)
        for index, value in horarios.iteritems():
            # llega a tiempo
            if self.convertir_fecha(value["min_entrada"]) <= fecha and fecha <= self.convertir_fecha(value["entrada"]):
                self.marcacion["entrada-"+index] = self.aTiempo(hora)
            # llega atrasado o tiene un permiso para llegar tarde
            elif fecha > self.convertir_fecha(value["entrada"]) and fecha < self.convertir_fecha(value["salida"]):
                # si esta entrando y es la primera vez en el dia que esta entrando desde=8:40 hasta=hora_llegada se genera un posible permiso o atraso segun
                if permiso == "entrada" and contador == 1:
                    self.diccionario_permiso["desde"] = value["entrada"]
                    self.diccionario_permiso["hasta"] = hora
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}
                # si esta entrando seguramente de algun permiso que tuvo (hasta)
                if permiso == "entrada"and  contador > 1:
                    self.diccionario_permiso["hasta"] = hora
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}
                #si esta saliendo durante la mañana se genera un permiso (desde)
                if permiso == "salida":
                    self.diccionario_permiso["desde"] = hora


                
                    
            elif fecha >= self.convertir_fecha(value["salida"]) and fecha <= self.convertir_fecha(value["max_salida"]):
                self.marcacion["salida-"+index] = hora
                if len(self.diccionario_permiso) == 1:
                    self.diccionario_permiso["hasta"] = value["salida"]
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}
                if not self.marcacion["entrada-"+index] and not self.marcacion["permisos"]:
                    self.diccionario_permiso["desde"] = value["entrada"]
                    self.diccionario_permiso["hasta"] = value["salida"]
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}
                    
    # caso (no marco ni entrada ni salida)
    def noMarcado(self, horarios, json_marcado, turno):
        for index, value in horarios.iteritems():
            if index == turno:
                self.diccionario_permiso["desde"] = value["entrada"]
                self.diccionario_permiso["salida"] = value["salida"]
                self.marcacion["permisos"].append(self.diccionario_permiso)
                self.diccionario_permiso = {}
                

    def marcadoTurno(self, horarios, horas, turno):
        horas_registradas = []
        for hora in horas:
            if hora > horarios[turno]["min_entrada"] and hora < horarios[turno]["max_salida"]:
                horas_registradas.append(hora)
        return horas_registradas
        

    #principal
    def main(self, horas, uid, fecha, dispositivo):
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
        
        json_marcado = {
            "marcado":[],
        }

        #llena de datos basicos uid, fecha, dispositivo
        json_marcado["uid"] = uid
        json_marcado["fecha"] = fecha
        json_marcado["dispositivo"] = dispositivo
        
        
        #separa las horas en turnos

        horasM = self.marcadoTurno(horarios, horas, "manana")
        horasT = self.marcadoTurno(horarios, horas, "tarde")

        
        #mañana
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
            
                
        # ---------------     verificando si olvido marcar  -----------------------------
        # verificar esta parte para los casos en que el usuario llega tarde y no marca salida
        # verificar para que cuando llega temprano y no marca salida solo le de un permiso desde la hora de entrada valida
        for index, value in horarios.iteritems():
            if not self.marcacion["salida-"+index]:
                if not self.marcacion["entrada-"+index]:
                    self.diccionario_permiso["desde"] = value["entrada"]
                    self.diccionario_permiso["hasta"] = value["salida"]
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}
                # elif len(self.marcacion["permisos"]) > 0:
                #     tamanho = len(self.marcacion["permisos"])
                #     print "aqui viene",self.marcacion["permisos"][tamanho-1]
                #     for campo, permiso_registrado in self.marcacion["permisos"][tamanho-1].iteritems():
                #         if campo == "hasta":
                #             print campo, permiso_registrado
                elif len(self.diccionario_permiso) > 0:
                    self.diccionario_permiso["hasta"] = value["salida"]
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}
                else:
                    self.diccionario_permiso["desde"] = self.marcacion["entrada-"+index]
                    self.diccionario_permiso["hasta"] = value["salida"]
                    self.marcacion["permisos"].append(self.diccionario_permiso)
                    self.diccionario_permiso = {}
                    
        json_marcado["marcado"].append(self.marcacion)
                    
                
                
        #print json.dumps(json_marcado, sort_keys=True, indent=4)
        return json_marcado
            
            



#ejemplo de horas
#horas =["14:30:00","16:30:00", "19:00:00"]
#marcado = Marcado()
#marcado.main(horas)
