from datetime import datetime
import recovery.actions.funcsDate as fD
from recovery.dal.classesDtype import dtype as dt

class readConfig:
    def __init__(self, path, file, minDate):
        self.path = path
        self.file = file
        self.f = open(path + "\\" +  file, encoding="utf8")
        self.minDate = minDate
        self.configDic = {}        
    def read2Dic(self):
        line = str(self.f.readline())
        dateTime = line.split(" ")
        self.configDic['startDate'] = datetime.strptime(dateTime[0], dt.fmtDate) 
        self.configDic['startTime'] = datetime.strptime(dateTime[1], dt.fmtTime) 
        self.configDic['endDate'] = datetime.strptime(dateTime[2], dt.fmtDate) 
        self.configDic['endTime'] = datetime.strptime(dateTime[3], dt.fmtTime) 
        startDateTime = datetime.combine(datetime.date(self.configDic['startDate']), datetime.time(self.configDic['startTime']))
        endDateTime = datetime.combine(datetime.date(self.configDic['endDate']), datetime.time(self.configDic['endTime']))
        self.configDic['startInt'] = fD.dateDiffMin(startDateTime, self.minDate)
        self.configDic['endInt'] = fD.dateDiffMin(endDateTime, self.minDate)
        line = str(self.f.readline())
        self.readLine2Dic(line, 'delay')
        line = str(self.f.readline())
        self.readLine2Dic(line, 'cancelA')
        line = str(self.f.readline())
        self.readLine2Dic(line, 'cancelR')
        line = str(self.f.readline())
        array = line.split(" ")
        arraySize = len(array)
        n = 0
        key = 'downgrade'
        while n < arraySize - 1 : #remove \n
            cabin = array[n]
            cabinInt = dt.cabinInt[cabin]
            n += 1
            cabin = array[n]
            _cabinInt = dt.cabinInt[cabin]
            n += 1
            dist = array[n]
            distInt = dt.distInt[dist]
            n += 1
            value = array[n]
            self.configDic[key, cabinInt, _cabinInt, distInt] = float(value) 
            n += 1
        return self.configDic
    #insert coeff.    
    def readLine2Dic(self, line, key):
        array = line.split(" ")
        arraySize = len(array)
        n = 0
        while n < arraySize - 1 : #remove \n
            cabin = array[n]
            cabinInt = dt.cabinInt[cabin]
            n += 1
            dist = array[n]
            distInt = dt.distInt[dist]
            n += 1
            value = float(array[n])
            #self.configDic[key][cabinInt*10+distInt] = value
            self.configDic[key, cabinInt, distInt] = value
            n += 1