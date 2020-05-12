import pdb
import datetime
from recovery.dal.classesDtype import dtype as dt
import numpy as np


def verifyFlightRanges(flightRanges, rotation, index):
    if len(flightRanges) != len(rotation[index:]):
        print("No. ranges diff. remaining flights")
        import pdb; pdb.set_trace()

def verifyCombo(combo, rotation, index):
    if(len(combo) != len(rotation[index:])):
        print("Combo size is diff. from remaining rotation")
        import pdb; pdb.set_trace()

def verifyRotation(rotation, movingFlights, fixedFlights, index):
    if len(rotation) != len(rotation[:index]) + len(movingFlights) + len(fixedFlights):
        print("Diff. in length")
        import pdb; pdb.set_trace()

def value(combo):
    noCancel = sum([t for t in combo if t == -1])
    totalDelay = sum([t for t in combo if t > 0])
    return noCancel, totalDelay, combo

def saveAirportCap(flightSchedule, airportCap): #update the airp. cap.
    for flight in flightSchedule[(flightSchedule['flight'] != '') & (flightSchedule['cancelFlight'] != 1)]:
        if flight['cancelFlight'] == 1:
            print("Airport capacity cancelled flight update")
            import pdb; pdb.set_trace()
        #update airp. dep. cap.
        index = int(flight['altDepInt']/60)
        airportCap[flight['origin']][index]['noDep'] += 1
        #update airp. arr. cap.
        index = int(flight['altArrInt']/60)
        airportCap[flight['destination']][index]['noArr'] += 1
    return airportCap

def newRotation(combo, rotation): 
    i = 0
    for delay, flight in zip(combo, rotation):
        if len(combo) != len(rotation):
            print("Diff. size between combo and rotation")
            import pdb; pdb.set_trace()

        if delay == -1: #cancel the flight
            flight['cancelFlight'] = 1
        else:
            flight['altDepInt'] += delay
            flight['altArrInt'] += delay
        rotation[i] = flight #update the rotation
        i += 1

def cost(solutionARP, itineraryDic):
    pass

def export(flightScheduleSA, itineraryDic, minDate, path):
    sb = ""
    for fSA in flightScheduleSA:

        fSA = fSA[fSA['origin'] != ''] #this will remove the maint.
        for fRA in fSA:
            idFlight = fRA['flight'][:-8]
            date = datetime.datetime.strptime(fRA['flight'][len(idFlight):], dt.fmtDate) #convert to date
                                
            originFlight = fRA['origin']
            destinationFlight = fRA['destination']
            altDepInt = fRA['altDepInt']
            
            noDays = int(altDepInt / (60*24))
            noHours = int((altDepInt - noDays*60*24)/60)
            noMinutes = (altDepInt - noDays*60*24 - noHours*60)
            altDepDate = minDate + datetime.timedelta(days = noDays)
            altDepTime = datetime.datetime.strptime(str(noHours) + ":" + str(noMinutes), dt.fmtTime)

            altArrInt = fRA['altArrInt']
            noDays = int(altArrInt / (60*24))
            noHours = int((altArrInt - noDays*60*24)/60)
            noMinutes = (altArrInt - noDays*60*24 - noHours*60)
            altArrDate = minDate + datetime.timedelta(days = noDays)
            altArrTime = datetime.datetime.strptime(str(noHours) + ":" + str(noMinutes), dt.fmtTime)
            
            previous = fRA['previous']
            try:    
                if (altDepDate - date).days > 0:
                    depNextDay = "+" + str((altDepDate - date).days) #fRA deleted
                else:
                    depNextDay = ""

                if (altArrDate - date).days > 0:
                    arrNextDay = "+" + str((altArrDate - date).days)
                else:
                    arrNextDay = ""
            except:
                print("Exception finding export@solution.py")
                import pdb; pdb.set_trace()
            cancelFlight = fRA['cancelFlight']
            aircraft = fRA['aircraft']
            if (cancelFlight == 1):
                aircraft = "cancelled"
            sb += (str(idFlight) + " " + originFlight + " " + destinationFlight + " " +
                    str(altDepTime.strftime(dt.fmtTime)) + depNextDay + " " + str(altArrTime.strftime(dt.fmtTime)) + arrNextDay + " " + str(previous) + " " +
                    str(date.strftime(dt.fmtDate)) + " " + aircraft)
            sb += "\n"

    sb += "#"
    # write string to sol_rotation
    text_file = open(path+"\\sol_rotations.csv", "w")
    text_file.write(sb)
    text_file.close()

    
    sb = ""
    for itinerary, fs in itineraryDic.items(): #fs flightSchedule
        #try:
        sb += str(itinerary) + " " + fs['typeItinerary'] + " " + str(fs['price']) + " " + str(fs['count'])
        #i.sort(key = lambda r: r.altDepInt) 
        _fs = fs['flightSchedule']
        _fs = np.sort(_fs, order = 'flightIndex')
        for f in _fs:
            if f['cancelFlight'] == 0: #add cancel flight because a flight can be cancell. in the middle of the rot. 
                # the sol. that makes the itin. feas. needs to cancel the remain. flights in the itin.
                idFlight = f['flight'][:-8]
                date = f['flight'][len(idFlight):]
                cabin = dt.cabin[f['cabin']] #cabin converter dict.
                sb += " " + idFlight + " " + date + " " + cabin  
            else:
                sb += " cancelled "
                break
        #except Exception as ex:
            #print(ex)
            #pdb.set_trace()   
        sb += "\n"
    sb += "#"
    text_file = open(path+"\\sol_itineraries.csv", "w")
    text_file.write(sb)
    text_file.close()