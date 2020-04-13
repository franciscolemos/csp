from dateutil import relativedelta
import datetime

def dateDiffDay(endDateTime, startDateTime):
    diffTime = relativedelta.relativedelta(endDateTime, startDateTime)
    return diffTime.days

def dateDiffMin(endDateTime, startDateTime):
    diffTime = relativedelta.relativedelta(endDateTime, startDateTime)
    time = diffTime.minutes
    time += diffTime.hours * 60
    time += diffTime.days * 60 * 24
    return time

def intToDate(refDate, intVal):
    pass

def intToTime(refDate, intVal):
    pass

def  dateDiffHour(endDateTime, startDateTime):
    diffTime = relativedelta.relativedelta(endDateTime, startDateTime)
    hours = diffTime.hours
    return hours

def  dateDiffDays(endDateTime, startDateTime):
    diffTime = relativedelta.relativedelta(endDateTime, startDateTime)
    days = diffTime.days
    return days

def minDate(rotationList):
     return min(r.date for r in rotationList)
 
def maxDate(rotationList):
    return max(r.date for r in rotationList)

def int2DateTime(_int, _minDate):
     noDays = int(_int / (60*24))
     noHours = int((_int - noDays*60*24)/60)
     noMinutes = (_int - noDays*60*24 - noHours*60)
     _date = _minDate + datetime.timedelta(days = noDays)
     _time = datetime.datetime.strptime(str(noHours) + ":" + str(noMinutes),'%H:%M')
     _dateTime = datetime.datetime.combine(_date, _time.time())
     return _dateTime

     
