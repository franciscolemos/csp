import recovery.dal.classesRoadef as ROADEF
from recovery.dal.classesDtype import dtype as dt
from datetime import datetime
import numpy as np
import csv

class readItineraries:
    def __init__(self, path, file):
        self.path = path
        self.file = file
        self.f = open(path + "/" +  file, encoding="utf8")
        self.fmtDate = dt.fmtDate
        self.dtypeItinFS = dt.dtypeItinFS0

    def read2Dic(self):
        with open(self.path + "/" +  self.file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=' ')
            line_count = 0
            itineraryDic = {}
            for itineraryLine in csv_reader:
                itineraryLine = list(filter(None, itineraryLine)) # clean empty values from list
                if itineraryLine[0] == "#":
                    return itineraryDic
                _n = len(itineraryLine)
                itinerary = ROADEF.itinerary()
                itinerary.idItinerary = int(itineraryLine[0])
                if itinerary.idItinerary % 1000 == 0:
                    print(itinerary.idItinerary ) 
                itinerary.typeItinerary = itineraryLine[1]
                itinerary.price = float(itineraryLine[2])
                itinerary.count = int(itineraryLine[3])
                itineraryDic[itinerary.idItinerary] = {'typeItinerary':itineraryLine[1], 'price':float(itineraryLine[2]), 'count':int(itineraryLine[3])}
                j =  4
                flightList = []
                index = 0
                while(j < _n):
                    itinerary.idFlight = str(itineraryLine[j]).strip()
                    j += 1
                    itinerary.date = str(itineraryLine[j]).strip()
                    j += 1
                    itinerary.cabin = str(itineraryLine[j]).strip() # F B E
                    cabinInt = dt.cabinInt[itinerary.cabin]
                    j += 1
                    flightList.append((index, str(itinerary.idFlight + itinerary.date), cabinInt, -1)) # 0 assumes the flight is not cancelled
                    index += 1
                flightSA = np.array(flightList, self.dtypeItinFS)
                itineraryDic[itinerary.idItinerary]['flightSchedule'] = flightSA
                
        return itineraryDic
                
# itineraryDic
# dtypeItinFS0= np.dtype([('flightIndex', np.uint8), ('flight', np.unicode, 13), ('cabin', np.int8), ('cancelFlight', np.uint8)])
