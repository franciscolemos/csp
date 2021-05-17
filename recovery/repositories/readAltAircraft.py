from datetime import datetime
import recovery.dal.classesRoadef as ROADEF
import recovery.actions.funcsDate as fD

class readAltAircraft:
    def __init__(self, path, file, minDate):
        self.path = path
        self.file = file
        self.f = open(path + "/" +  file, encoding="utf8")
        self.fmtDate = '%d/%m/%y'
        self.fmtTime = '%H:%M'
        self.minDate = minDate

    def read2Dic(self):
        altAircraftDic = {}
        with self.f as fp:  
            line = fp.readline()
            while line and str(line).strip() != "#":
                altAircraftLine = line.split(" ")
                altAircraft = ROADEF.altAircraft()
                altAircraft.aircraft = altAircraftLine[0]
                altAircraft.startDate = datetime.strptime(altAircraftLine[1].strip(), self.fmtDate)
                altAircraft.startTime = datetime.strptime(altAircraftLine[2].strip(), self.fmtTime)
                startDateTime = datetime.combine(datetime.date(altAircraft.startDate), datetime.time(altAircraft.startTime))
                altAircraft.startInt = fD.dateDiffMin(startDateTime, self.minDate) #conv. dep. datetime to int
                altAircraft.endDate = datetime.strptime(altAircraftLine[3].strip(), self.fmtDate)
                altAircraft.endTime = datetime.strptime(altAircraftLine[4].strip(), self.fmtTime)
                endDateTime = datetime.combine(datetime.date(altAircraft.endDate), datetime.time(altAircraft.endTime))
                altAircraft.endInt = fD.dateDiffMin(endDateTime, self.minDate) #conv. arr. datetime to int
                altAircraftDic[altAircraft.aircraft] = {'startDate': altAircraft.startDate, 'startTime':altAircraft.startTime, 'startInt': altAircraft.startInt,
                    'endDate':altAircraft.endDate, 'endTime':altAircraft.endTime, 'endInt':altAircraft.endInt}
                line = fp.readline()
        return altAircraftDic

