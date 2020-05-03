import recovery.dal.classesRoadef as ROADEF
from datetime import datetime
from recovery.dal.classesDtype import dtype as dt
import recovery.actions.funcsDate as fD
import numpy as np
import pdb
import sys
import os

class readAirports:
    def __init__(self, path, file, noDays, altAirportsSA, flightScheduleSA):
        self.path = path
        self.file = file
        self.f = open(path + "\\" +  file, encoding="utf8")
        self.fmtDate = dt.fmtDate
        self.fmtTime = dt.fmtTime
        self.dtype = np.dtype([('date', 'datetime64[D]'), 
            ('startTime', datetime), ('startInt', np.int16), 
            ('endTime', datetime), ('endInt', np.int16), 
            ('capDep', np.int16), ('capArr', np.int16),  
            ('noDep', np.int16), ('noArr', np.int16)])
        self.airportDic = {}
        self.noAirports = -1
        self.noDays = noDays # this will have importance for airp. cap. plan. horiz.
        self.altAirportsSA = altAirportsSA
        self.flightScheduleSA = flightScheduleSA
        self.dtypeCap = np.dtype([('airport', np.unicode, 3), 
            ('startInt', np.int16), ('endInt', np.int16),
            ('capDep', np.int16), ('capArr', np.int16),  
            ('noDep', np.int16), ('noArr', np.int16)])
        self.infeasCapDepSA = []
        self.infeasCapArrSA = []
        self.availCapDepSA = []
        self.availCapArrSA = []
    def read2Dic(self):
        with self.f as fp:  
           line = fp.readline()
           while line and str(line).strip() != "#" :
               airport = ROADEF.airport()
               airport.airport = line[:3]
               airport.depArr = line[4:]
               self.initializeDic(airport)
               line = fp.readline()
        self.noAirports = len(self.airportDic)
        return self.airportDic

    def initializeDic(self, airport):
        noDep = -1
        noArr = -1
        line = str(airport.depArr).rstrip().split(" ")
        size = int(len(line)/4) #size of the data
        tmpAirportSchedule = np.zeros(size, self.dtype) #initialize 
        size = self.noDays #size of the planning horizon
        airportSchedule = np.zeros(size * 24, self.dtype) #initialize 
        index = 0 #index for the airport
        i = 0
        while(index < len(line[:-1])): # load the temp. airp. schedule
            tmpAirportSchedule[i]['capDep'] = line[index]
            index += 1
            tmpAirportSchedule[i]['capArr'] = line[index]
            index += 1
            tmpAirportSchedule[i]['startTime'] = datetime.strptime(line[index], self.fmtTime)
            tmpAirportSchedule[i]['startInt'] = int(line[index].split(":")[0])
            index += 1
            tmpAirportSchedule[i]['endTime'] = datetime.strptime(line[index], self.fmtTime)
            tmpAirportSchedule[i]['endInt'] = 24 if int(line[index].split(":")[0]) == 0 else int(line[index].split(":")[0]) 
            index += 1
            i += 1

        #create the airp. schedule for the plann. horizon
        i = 0
        for d in range(0, self.noDays):
            for h in range(1,25): # 1:24
                airportSchedule[i]['startInt'] = (h-1)*60 + 60 * 24 * d
                airportSchedule[i]['endInt'] = h*60 + 60 * 24 * d
                _tmpAirportSchedule = tmpAirportSchedule[(tmpAirportSchedule['startInt'] <= h-1) & (tmpAirportSchedule['endInt'] >= h)]
                if len(self.altAirportsSA):
                    if len(self.altAirportsSA[ #check if there is disruption for the interval
                        (self.altAirportsSA['airport'] == airport.airport)  &  #airport
                        (self.altAirportsSA['startInt'] <= airportSchedule[i]['startInt']) & #start of disruption
                        (self.altAirportsSA['endInt'] >= airportSchedule[i]['endInt'])]) > 0: #end fo disruption

                        _tmpAirportSchedule = self.altAirportsSA[(self.altAirportsSA['airport'] == airport.airport) & #airport  
                            (self.altAirportsSA['startInt'] <= airportSchedule[i]['startInt']) & #start of disruption
                            (self.altAirportsSA['endInt'] >= airportSchedule[i]['endInt'])] #end of disruption

                airportSchedule[i]['capDep'] = _tmpAirportSchedule['capDep']
                airportSchedule[i]['capArr'] = _tmpAirportSchedule['capArr']
                if len(self.flightScheduleSA):
                    noDep = len(self.flightScheduleSA[(self.flightScheduleSA['origin'] == airport.airport ) &
                        (self.flightScheduleSA['altDepInt'] >= airportSchedule[i]['startInt']) &
                        (self.flightScheduleSA['altDepInt'] < airportSchedule[i]['endInt'])])
                    airportSchedule[i]['noDep'] = noDep

                    noArr = len(self.flightScheduleSA[(self.flightScheduleSA['destination'] == airport.airport ) &
                        (self.flightScheduleSA['altArrInt'] >= airportSchedule[i]['startInt']) &
                        (self.flightScheduleSA['altArrInt'] < airportSchedule[i]['endInt'])])
                    airportSchedule[i]['noArr'] = noArr
                i += 1
        self.airportDic[airport.airport] = airportSchedule

        
    def infeasCap(self):
        size = self.noAirports * self.noDays * 24
        self.infeasCapDepSA = np.zeros(size, self.dtypeCap) #intialize to plann. horizon size
        i = 0
        self.infeasCapArrSA = np.zeros(size, self.dtypeCap) #intialize to plann. horizon size
        j = 0
        for airport, airportSchedule in self.airportDic.items():
            timeSlots = airportSchedule[airportSchedule['noDep'] > airportSchedule['capDep']]
            if len(timeSlots) > 0:
                for tS in timeSlots:
                    self.infeasCapDepSA[i] = (airport, tS['startInt'], tS['endInt'], tS['capDep'], tS['capArr'], tS['noDep'], tS['noArr'])
                    i += 1
            timeSlots = airportSchedule[airportSchedule['noArr'] > airportSchedule['capArr']]
            if len(timeSlots) > 0:
                for tS in timeSlots:
                    self.infeasCapArrSA[i] = (airport, tS['startInt'], tS['endInt'], tS['capDep'], tS['capArr'], tS['noDep'], tS['noArr'])
                    j += 1

        self.infeasCapDepSA = self.infeasCapDepSA[self.infeasCapDepSA['airport']  != '']
        self.infeasCapArrSA = self.infeasCapArrSA[self.infeasCapArrSA['airport']  != '']

    def availCap(self):
        size = self.noAirports * self.noDays * 24
        self.availCapDepSA = np.zeros(size, self.dtypeCap) #intialize to plann. horizon size
        i = 0
        self.availCapArrSA = np.zeros(size, self.dtypeCap) #intialize to plann. horizon size
        j = 0
        for airport, airportSchedule in self.airportDic.items():
            timeSlots = airportSchedule[airportSchedule['noDep'] < airportSchedule['capDep']]
            if len(timeSlots) > 0:
                for tS in timeSlots:
                    self.availCapDepSA[i] = (airport, tS['startInt'], tS['endInt'], tS['capDep'], tS['capArr'], tS['noDep'], tS['noArr'])
                    i += 1
            timeSlots = airportSchedule[airportSchedule['noArr'] < airportSchedule['capArr']]
            if len(timeSlots) > 0:
                for tS in timeSlots:
                    self.availCapArrSA[i] = (airport, tS['startInt'], tS['endInt'], tS['capDep'], tS['capArr'], tS['noDep'], tS['noArr'])
                    j += 1

        self.availCapDepSA = self.availCapDepSA[self.availCapDepSA['airport']  != '']
        self.availCapArrSA = self.availCapArrSA[self.availCapArrSA['airport']  != '']