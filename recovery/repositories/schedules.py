from datetime import datetime
from datetime import timedelta
from recovery.dal.classesDtype import dtype as dt
import recovery.actions.funcsDate as fD
import recovery.dal.classesRoadef as ROADEF
import numpy as np


import sys
import os
import pdb


class initialize:
    def __init__(self, aircraftRotationDic,  altAircraftDic, 
        altFlightDic, aircraftDic, flightDic, 
        path, minDate):
        self.aircraftRotationDic = aircraftRotationDic
        self.altAircraftDic = altAircraftDic
        self.altFlightDic = altFlightDic
        self.aircraftDic = aircraftDic
        self.flightDic = flightDic
        self.flightScheduleSA = []
        self.dtypeFS = dt.dtypeFS
        self.aircraftScheduleDic = {}
        self.dtypeAS = dt.dtypeAS
        self.noFlights = 0
        self.path = path
        self.minDate = minDate
        self.fmtDate = dt.fmtDate


    def aircraftSchedule(self): #returns the flight schedule of each aircraft and the max no. of flights
        for aircraft, flightList in self.aircraftRotationDic.items():
            self.noFlights += len(flightList)
            size = len(flightList)
            if self.aircraftDic[aircraft].get('maintAirport', None) != None: #in  the case of maint.
                size += 1
            tmpFlightSchedule = np.zeros(size, self.dtypeAS)
            i = 0
            for flight in flightList: #flight = [idFlight+dateStr, roation.date]
                idFlight = int(flight[0][:-8]) #1st element
                date = flight[1] #date formated from the rotation
                origin = self.flightDic[idFlight]['origin']
                destination = self.flightDic[idFlight]['destination']
                previous = self.flightDic[idFlight]['previous']
                if (previous != '0'):
                    tt = self.aircraftDic[aircraft]['transitTime'] 
                else:
                    tt = self.aircraftDic[aircraft]['turnAround']
                depTime = self.flightDic[idFlight]['depTime']
                depDateTime = datetime.combine(datetime.date(date), depTime)
                arrTime = self.flightDic[idFlight]['arrTime']
                arrNextDay  = self.flightDic[idFlight].get('arrNextDay', 0)
                arrDateTime = datetime.combine(datetime.date(date + timedelta(days = arrNextDay)), arrTime)
                depInt = fD.dateDiffMin(depDateTime, self.minDate)
                arrInt = fD.dateDiffMin(arrDateTime, self.minDate)
                #insert flight disruption
                delay = 0
                if self.altFlightDic.get(flight[0], None) != None:
                    delay = self.altFlightDic[flight[0]]['delayAltFlight']
                if delay != 0:
                    if delay == -1: #cancelled flight
                        altDepInt = depInt #in the case of flight creation
                        altArrInt = arrInt #in the case of flight creation
                        cancelFlight = 1
                    else: #delayed flights
                        cancelFlight = 0 #aircraft is delayed but still flying
                        altDepInt = depInt + delay
                        altArrInt = arrInt + delay
                else: #no flight disruption
                        cancelFlight = 0
                        altDepInt = depInt
                        altArrInt = arrInt
                #insert aircraft disruption
                broken = 0
                if self.altAircraftDic.get(aircraft, None)  != None:
                    startInt = self.altAircraftDic[aircraft]['startInt']
                    endInt = self.altAircraftDic[aircraft]['endInt']
                    if (altDepInt >= startInt and altDepInt <= endInt):
                        broken = -1 
                        cancelFlight = 1

                tmpFlightSchedule[i] = (flight[0], idFlight, date, origin, depInt, altDepInt, destination, arrInt, altArrInt, previous, tt,  delay, broken, cancelFlight)
                i += 1
                
            if self.aircraftDic[aircraft].get('maintAirport', None) != None: #introduce the maint. schedule
                maintAirport = self.aircraftDic[aircraft]['maintAirport']
                maintStartDate = self.aircraftDic[aircraft]['maintStartDate']
                maintStartInt = self.aircraftDic[aircraft]['maintStartInt']
                maintEndInt = self.aircraftDic[aircraft]['maintEndInt']
                tmpFlightSchedule[i] = ('m', 'm', maintStartDate, maintAirport, maintStartInt, maintStartInt, maintAirport, maintEndInt, maintEndInt, '0', 0,  0, 0, 0)
            
            noCancelFlights = len(tmpFlightSchedule[tmpFlightSchedule['cancelFlight'] == 1]) #to create an struct. array to accomm. cancelled flights
            if noCancelFlights > 0:
                self.noFlights += noCancelFlights #get the total size of the available flights
                flightSchedule = np.zeros(size + noCancelFlights, self.dtypeAS) #create a new struct. array
                y = len(tmpFlightSchedule)
                flightSchedule[0:y] = tmpFlightSchedule #copy the array to part fo the array
                self.aircraftScheduleDic[aircraft] = flightSchedule
            else:    
                self.aircraftScheduleDic[aircraft] = tmpFlightSchedule
    def flightSchedule(self): #for the purpose of calculating no. dep. and no. arr.
        self.flightScheduleSA = np.zeros(self.noFlights, self.dtypeFS) #initialize the struct. array
        i = 0
        for aircraft, flightArray in self.aircraftScheduleDic.items():
            for flight in flightArray[flightArray['flight'] != 'm']: #exclude maintenance
                self.flightScheduleSA[i]['aircraft'] = aircraft
                self.flightScheduleSA[i]['family'] = self.aircraftDic[aircraft]['family']
                self.flightScheduleSA[i]['flight'] = flight['flight']
                self.flightScheduleSA[i]['origin'] = flight['origin']
                self.flightScheduleSA[i]['depInt'] = flight['depInt']
                self.flightScheduleSA[i]['altDepInt'] = flight['altDepInt']
                self.flightScheduleSA[i]['destination'] = flight['destination']
                self.flightScheduleSA[i]['arrInt'] = flight['arrInt']
                self.flightScheduleSA[i]['altArrInt'] = flight['altArrInt']
                self.flightScheduleSA[i]['previous'] = flight['previous']
                self.flightScheduleSA[i]['tt'] = flight['tt']
                self.flightScheduleSA[i]['altFlight'] = flight['delay'] #('altFlight', np.int16), ('altAirc', np.uint8), ('newFlight', np.uint8)
                self.flightScheduleSA[i]['altAirc'] = flight['broken']
                self.flightScheduleSA[i]['newFlight'] = 0
                self.flightScheduleSA[i]['cancelFlight'] = flight['cancelFlight']
                i += 1