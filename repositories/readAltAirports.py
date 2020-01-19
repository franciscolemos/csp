from datetime import datetime
import dal.classesRoadef as ROADEF
import actions.funcsDate as fD
import numpy as np
from numpy import genfromtxt
import pdb
import os

class readAltAirport:

    def __init__(self, path, file, minDate):
        self.path = path
        self.file = file
        self.f = open(path + "\\" +  file, encoding="utf8")
        self.fmtDate = '%d/%m/%y'
        self.fmtTime = '%H:%M'
        self.altAirportsSA = []
        self.dtypeA = np.dtype([('airport', np.unicode, 3), ('startDate', np.unicode, 8), ('startTime', np.unicode, 5), ('endDate', np.unicode, 8), ('endTime', np.unicode, 5), 
                        ('capDep', np.int8), ('capArr', np.int8)])
        self.dtypeAA = np.dtype([('airport', 'S3'), ('startDateTime', datetime ), ('startInt', np.int16), ('endDateTime', datetime),
            ('endInt', np.int16), ('capDep', np.int8), ('capArr', np.int8)])
        self.minDate = minDate
 
    def read2SA(self):
        #if os.stat(self.path + "\\" +  self.file).st_size > 3: #prevent the warning from showing
        tmpAltAirports = genfromtxt(self.path + "\\" +  self.file, delimiter=' ', dtype = self.dtypeA)
        size = tmpAltAirports.size
        if(size > 0):
            self.altAirportsSA = np.zeros(size, self.dtypeAA) #initialize the struct. array
            i = 0 
            for altAirportLine in np.nditer(tmpAltAirports): #
                self.altAirportsSA[i]['airport'] = altAirportLine['airport']
                startDate = datetime.strptime(str(altAirportLine['startDate']), self.fmtDate)
                startTime = datetime.strptime(str(altAirportLine['startTime']), self.fmtTime)
                self.altAirportsSA[i]['startDateTime'] = datetime.combine(datetime.date(startDate), datetime.time(startTime))
                self.altAirportsSA[i]['startInt'] = fD.dateDiffMin(self.altAirportsSA[i]['startDateTime'], self.minDate)
                endDate = datetime.strptime(str(altAirportLine['endDate']), self.fmtDate)
                endTime = datetime.strptime(str(altAirportLine['endTime']), self.fmtTime)
                self.altAirportsSA[i]['endDateTime'] = datetime.combine(datetime.date(endDate), datetime.time(endTime))
                self.altAirportsSA[i]['endInt'] = fD.dateDiffMin(self.altAirportsSA[i]['endDateTime'], self.minDate)
                self.altAirportsSA[i]['capDep'] = int(altAirportLine['capDep'])
                self.altAirportsSA[i]['capArr'] = int(altAirportLine['capArr'])
                i += 1
            return self.altAirportsSA
