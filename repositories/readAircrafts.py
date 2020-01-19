import sys
import os
from dal.classesRoadef import aircraft
from datetime import datetime
from datetime import timedelta
from dal.classesDtype import dtype as dt
import dal.classesRoadef as ROADEF
import actions.funcsDate as fD

class readAircrafts:
    def __init__(self, path, file, minDate):
        self.path = path
        self.file = file
        self.f = open(path + "\\" +  file, encoding="utf8")
        self.fmtDate = dt.fmtDate # '%d/%m/%y'
        self.fmtTime = dt.fmtTime # '%H:%M'
        self.minDate = minDate

    def read2Dic(self):
        aircraftDic = {}
        with self.f as fp:  
            line = fp.readline()
            while line and str(line).strip() != "#" :
                aircraftLine = line.split(" ")
                aircraft = ROADEF.aircraft()
                aircraft.aircraft = aircraftLine[0].rstrip() 
                aircraft.family = aircraftLine[1].rstrip()
                aircraft.model = aircraftLine[2].rstrip()
                cabinLine = aircraftLine[3].split("/")
                aircraft.F = cabinLine[0]
                aircraft.B = cabinLine[1]
                aircraft.E = cabinLine[2]
                aircraft.rangeHours = int(aircraftLine[4])
                aircraft.hourOperatingCost = float(aircraftLine[5])
                aircraft.turnAround = int(aircraftLine[6])
                aircraft.transitTime = int(aircraftLine[7])
                aircraft.originAirport = aircraftLine[8]
                
                aircraftDic[aircraft.aircraft] = {'family':aircraft.family, 'model':aircraft.model, 'F':aircraft.F, 'B':aircraft.B,
                    'E':aircraft.E, 'rangeHours':aircraft.rangeHours, 'hourOperatingCost':aircraft.hourOperatingCost,
                    'turnAround':aircraft.turnAround, 'transitTime':aircraft.transitTime, 'originAirport':aircraft.originAirport}
                
                if(aircraftLine[9].rstrip() != "NULL" ):
                    maintLine = aircraftLine[9].split("-")
                    aircraft.maintAirport = maintLine[0]
                    aircraft.maintStartDate = datetime.strptime(maintLine[1], self.fmtDate)
                    aircraft.maintStartTime = datetime.strptime(maintLine[2], self.fmtTime)
                    maintStartDateTime = datetime.combine(datetime.date(aircraft.maintStartDate), datetime.time(aircraft.maintStartTime))
                    aircraft.maintStartInt = fD.dateDiffMin(maintStartDateTime, self.minDate)
                    aircraft.maintEndDate = datetime.strptime(maintLine[3], self.fmtDate)
                    aircraft.maintEndTime = datetime.strptime(maintLine[4], self.fmtTime)
                    maintEndDateTime = datetime.combine(datetime.date(aircraft.maintEndDate), datetime.time(aircraft.maintEndTime))
                    aircraft.maintEndInt = fD.dateDiffMin(maintEndDateTime, self.minDate)
                    aircraft.maintDuration = int(maintLine[5])
                
                    aircraftDic[aircraft.aircraft]['maintAirport'] = aircraft.maintAirport
                    aircraftDic[aircraft.aircraft]['maintStartDate'] = aircraft.maintStartDate
                    aircraftDic[aircraft.aircraft]['maintStartTime'] = aircraft.maintStartTime
                    aircraftDic[aircraft.aircraft]['maintStartInt'] = aircraft.maintStartInt
                    aircraftDic[aircraft.aircraft]['maintEndDate'] = aircraft.maintEndDate
                    aircraftDic[aircraft.aircraft]['maintEndTime'] = aircraft.maintEndTime
                    aircraftDic[aircraft.aircraft]['maintEndInt'] = aircraft.maintEndInt
                    aircraftDic[aircraft.aircraft]['maintDuration'] = aircraft.maintDuration
                
                line = fp.readline()
        return aircraftDic
