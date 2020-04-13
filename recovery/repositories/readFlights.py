import recovery.dal.classesRoadef as ROADEF
from datetime import datetime
import recovery.actions.funcsDate as fD

class readFlights:
    def __init__(self, path, file):
        self.path = path
        self.file = file
        self.flightDic = {}
        self.f = open(path + "\\" +  file, encoding="utf8")
        self.fmtDate = '%d/%m/%y'
        self.fmtTime = '%H:%M'


    def read2Dic(self):
        flightDic = {}
        with self.f as fp:  
           line = fp.readline()
           while line and str(line).strip() != "#" :
                flightLine = line.split(" ")
                flight = ROADEF.flight()
                flight.idFlight = int(str(flightLine[0]).strip())
                flight.origin = str(flightLine[1]).strip()
                flight.destination = str(flightLine[2]).strip()
                flight.depTime = datetime.strptime(flightLine[3], self.fmtTime).time()#conv. from str. to time
                #convert departure to integer
                flight.depInt = flight.depTime.hour*60 + flight.depTime.minute
                self.flightDic[flight.idFlight] = {'origin':flight.origin, 'destination':flight.destination, 
                    'depTime':flight.depTime, 'depInt':flight.depInt}
                #arrival on the next day
                if("+" in flightLine[4]):
                    tmpArrTime = flightLine[4].split("+")
                    flight.arrTime = datetime.strptime(tmpArrTime[0], self.fmtTime).time()#conv. from str. to time
                    flight.arrNextDay = int(tmpArrTime[1])
                    self.flightDic[flight.idFlight]['arrNextDay'] = flight.arrNextDay
                    #single time frame later on to used in aircraftRotationDic initialization
                    flight.arrInt = 24*60 + flight.arrTime.hour*60 + flight.arrTime.minute
                else:
                    flight.arrTime = datetime.strptime(flightLine[4], self.fmtTime).time()#conv. from str. to time
                    #convert arrival to integer
                    flight.arrInt = flight.arrTime.hour*60 + flight.arrTime.minute
                flight.previous = str(flightLine[5]).strip()
                self.flightDic[flight.idFlight]['arrTime'] = flight.arrTime
                self.flightDic[flight.idFlight]['arrInt'] = flight.arrInt
                self.flightDic[flight.idFlight]['previous'] = flight.previous      
                line = fp.readline()
        return self.flightDic

