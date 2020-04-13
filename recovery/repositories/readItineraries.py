import recovery.dal.classesRoadef as ROADEF
from recovery.dal.classesDtype import dtype as dt
from datetime import datetime
import numpy as np

class readItineraries:
    def __init__(self, path, file):
        self.path = path
        self.file = file
        self.f = open(path + "\\" +  file, encoding="utf8")
        self.fmtDate = dt.fmtDate
        self.dtypeItinFS = dt.dtypeItinFS

    
    def read2Dic(self, flightScheduleSA, distSA):
        itineraryDic = {}
        with self.f as fp:  
            line = fp.readline()
            while line and str(line).strip() != "#" :
                itineraryLine = line.rstrip().split(" ")
                n = len(itineraryLine)
                itinerary = ROADEF.itinerary()
                itinerary.idItinerary = int(itineraryLine[0])
                itinerary.typeItinerary = itineraryLine[1]
                itinerary.price = float(itineraryLine[2])
                itinerary.count = int(itineraryLine[3])
                itineraryDic[itinerary.idItinerary] = {'typeItinerary':itineraryLine[1], 'price':float(itineraryLine[2]), 'count':int(itineraryLine[3])}
                j =  4
                flightList = []
                flightIndex = 0
                while(j < n):
                    #itinerary.idFlight = int(itineraryLine[j])
                    itinerary.idFlight = str(itineraryLine[j]).strip()
                    j += 1
                    #itinerary.date = datetime.strptime(itineraryLine[j], self.fmtDate) 
                    #itinerary.date = str(itineraryLine[j]).strip().replace("/","") 
                    itinerary.date = str(itineraryLine[j]).strip()
                    j += 1
                    itinerary.cabin = str(itineraryLine[j]).strip() # F B E
                    j += 1
                    #itineraryDic[itinerary.idItinerary][flight] = {'idFlight':itinerary.idFlight, 'date':itinerary.date, 'cabin':itinerary.cabin}
                    #itineraryDic[itinerary.idItinerary][flight] = {'idFlightDate':itinerary.idFlight + itinerary.date, 'cabin':itinerary.cabin}
                    flightRow = flightScheduleSA[flightScheduleSA['flight'] == itinerary.idFlight + itinerary.date] #find flight = [idFlight+dateStr, roation.date] 
                    origin = flightRow['origin'][0]
                    destination = flightRow['destination'][0]
                    trip = distSA['trip'][(distSA['origin'] == origin) & (distSA['destination'] == destination)]
                    #import pdb; pdb.set_trace()
                    flightList.append((flightIndex, flightRow['flight'][0], dt.cabinInt[itinerary.cabin], trip[0], flightRow['aircraft'][0],
                        flightRow['origin'][0], flightRow['depInt'][0], flightRow['altDepInt'][0], 
                        flightRow['destination'][0], flightRow['arrInt'][0], flightRow['altArrInt'][0], 
                        flightRow['previous'][0], flightRow['cancelFlight'][0], flightRow['cancelFlight'][0]))
                    flightIndex += 1

                flightSA = np.array(flightList, dtype = self.dtypeItinFS) #conv. the list into a struct. array
                itineraryDic[itinerary.idItinerary]['typeItinerary'] = itinerary.typeItinerary
                itineraryDic[itinerary.idItinerary]['price'] = itinerary.price
                itineraryDic[itinerary.idItinerary]['count'] = itinerary.count
                itineraryDic[itinerary.idItinerary]['flightSchedule'] = flightSA 
                line = fp.readline()
        return itineraryDic
          
