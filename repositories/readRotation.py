import dal.classesRoadef as ROADEF
from datetime import datetime

class readRotation:
    def __init__(self, path, file):
        self.path = path
        self.file = file
        self.f = open(path + "\\" +  file, encoding="utf8")
        self.fmtDate = '%d/%m/%y'
    def read2FlightRotationDic(self):
        rotationDic = {}
        minDate = datetime(9999, 12, 31)
        maxDate = datetime(1900, 1, 1)
        with self.f as fp:  
            line = fp.readline()
            while line and str(line).strip() != "#" :
                rotationLine = line.split(" ")
                rotation = ROADEF.rotation()
                #rotation.idFlight = int(rotationLine[0])
                rotation.idFlight = str(rotationLine[0]).strip()
                dateStr = str(rotationLine[1].strip())
                rotation.date = datetime.strptime(dateStr, self.fmtDate)
                if rotation.date < minDate:
                    minDate = rotation.date
                if rotation.date > maxDate:
                    maxDate = rotation.date
                #rotation.date = str(rotationLine[1]).strip().replace("/", "")
                rotation.aircraft = rotationLine[2].strip()
                rotationDic[rotation.idFlight + dateStr] = {'aircraft': rotation.aircraft}
                line = fp.readline()
        rotationDic['minDate'] = minDate
        rotationDic['maxDate'] = maxDate
        return rotationDic
    def read2AircraftRotationDic(self):
        rotationDic = {}
        with self.f as fp:  
            line = fp.readline()
            rotationLine = line.split(" ")
            while line and str(line).strip() != "#" :
                rotation = ROADEF.rotation()
                rotation.idFlight = str(rotationLine[0]).strip()
                #rotation.date = str(rotationLine[1]).strip().replace("/", "")
                dateStr = str(rotationLine[1].strip())
                rotation.date = datetime.strptime(dateStr, self.fmtDate)
                rotation.aircraft = str(rotationLine[2].strip())
                if (rotationDic.get(rotation.aircraft, None) == None):
                    flightList = []
                    flightList.append([rotation.idFlight + dateStr, rotation.date])
                    rotationDic[rotation.aircraft] = flightList
                else:
                    rotationDic[rotation.aircraft].append([rotation.idFlight + dateStr, rotation.date])
                line = fp.readline()
                rotationLine = line.split(" ") # read the next line
        return rotationDic
