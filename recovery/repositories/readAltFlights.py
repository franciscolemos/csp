from datetime import datetime
import recovery.dal.classesRoadef as ROADEF

class readAltFlights:
    def __init__(self, path, file):
        self.path = path
        self.file = file
        self.f = open(path + "/" +  file, encoding="utf8")
        self.fmtDate = '%d/%m/%y'
    def read2List(self):
        altFlightsList = []
        with self.f as fp:  
           line = fp.readline()
           while line and str(line).strip() != "#":
               altFlightsLine = line.split(" ")
               altFlight = ROADEF.altFlight()
               altFlight.idAltFlight = int(altFlightsLine[0])
               altFlight.depDateAltFligth =  datetime.strptime(altFlightsLine[1], self.fmtDate)
               altFlight.delayAltFlight = int(altFlightsLine[2])
               altFlightsList.append(altFlight)
               line = fp.readline()
        return altFlightsList
    def read2Dic(self):
        altFlightsDic = {}
        with self.f as fp:  
            line = fp.readline()
            while line and str(line).strip() != "#":
                altFlightsLine = line.split(" ")
                altFlight = ROADEF.altFlight()
                #altFlight.idAltFlight = int(altFlightsLine[0])
                altFlight.idAltFlight = str(altFlightsLine[0]).strip()
                #altFlight.depDateAltFligth =  datetime.strptime(altFlightsLine[1], self.fmtDate)
                #altFlight.depDateAltFligth =  str(altFlightsLine[1]).strip().replace("/","")
                altFlight.depDateAltFligth =  str(altFlightsLine[1]).strip()
                altFlight.delayAltFlight = int(altFlightsLine[2])
                altFlightsDic[altFlight.idAltFlight+altFlight.depDateAltFligth ] = {'delayAltFlight':altFlight.delayAltFlight}
                line = fp.readline()
        return altFlightsDic


