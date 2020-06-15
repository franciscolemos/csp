import pdb
import datetime
from recovery.dal.classesDtype import dtype as dt
import numpy as np

def verifyFlightRanges(flightRanges, rotation, index):
    if len(flightRanges) != len(rotation[index:]):
        print("No. ranges diff. remaining flights verifyFlightRanges@solution.py")
        import pdb; pdb.set_trace()

def verifyCombo(combo, rotation, index):
    if(len(combo) != len(rotation[index:])):
        print("Combo size is diff. from remaining rotation verifyCombo@solution.py")
        import pdb; pdb.set_trace()

def verifyRotation(rotation, movingFlights, fixedFlights, index):
    if len(rotation) != len(rotation[:index]) + len(movingFlights) + len(fixedFlights):
        print("Diff. in rotation length verifyRotation@solution.py")
        import pdb; pdb.set_trace()

def verifySingletonSol(size, solutionARP, flightSchedule):
    if size != len(solutionARP) + len(flightSchedule):
        print("Diff. in solutionARP length verifySingletonSol@solution.py")
        import pdb; pdb.set_trace()

def value(combo):
    noCancel = sum([t for t in combo if t == -1])
    totalDelay = sum([t for t in combo if t > 0])
    return noCancel, totalDelay, combo

def singletonRecovery(solutionARP, singletonList, airpCapCopy, aircraftSolList, configDic):
    solutionARP = np.concatenate(solutionARP).ravel() #flatten list of numpy arrays
    #import pdb; pdb.set_trace() #check if solutionARP is updated
    for singleton in singletonList: #remove the flights
        if singleton[1] == 'dep':
            startInt = 60 * int(singleton[0]['altDepInt']/60) #find the start of the time slot of the dep.
            endInt = startInt + 60
            origin = singleton[0]['origin']
            flight2Cancel = solutionARP[(solutionARP['origin'] == origin) & (solutionARP['cancelFlight'] == 0)] #find the origin of flight to be cancelled
            flight2Cancel = flight2Cancel[(flight2Cancel['altDepInt'] >= startInt) & (flight2Cancel['altDepInt'] < endInt) ]
            
            #import pdb; pdb.set_trace()
            if updateMulti(flight2Cancel, airpCapCopy, solutionARP, aircraftSolList, configDic) == -1:
                return -1
            #import pdb; pdb.set_trace()

        if singleton[1] == 'arr':
            startInt = 60 *  int(singleton[0]['altArrInt']/60) #find the start of the time slot of the arr.
            endInt = startInt + 60
            destination = singleton[0]['destination']
            flight2Cancel = solutionARP[(solutionARP['destination'] == destination) & (solutionARP['cancelFlight'] == 0)] #find the origin of flight to be cancelled
            flight2Cancel = flight2Cancel[(flight2Cancel['altArrInt'] >= startInt) & (flight2Cancel['altArrInt'] < endInt) ]
            
            #import pdb; pdb.set_trace()
            if updateMulti(flight2Cancel, airpCapCopy, solutionARP, aircraftSolList, configDic) == -1:
                return -1
            #import pdb; pdb.set_trace()

def airpCapRemove(flightSchedule, airportCap):
    #import pdb; pdb.set_trace()
    for flight in flightSchedule[(flightSchedule['flight'] != '') & (flightSchedule['cancelFlight'] != 1)]:
        if flight['cancelFlight'] == 1:
            print("Airport capacity cancelled flight update airpCapRemove@solution.py")
            import pdb; pdb.set_trace()
            continue
        #update airp. dep. cap.
        index = int(flight['altDepInt']/60)
        airportCap[flight['origin']][index]['noDep'] -= 1
        #update airp. arr. cap.
        index = int(flight['altArrInt']/60)
        airportCap[flight['destination']][index]['noArr'] -= 1
    return airportCap

def rotationRemove(flightSchedule, solutionARP):
    #import pdb; pdb.set_trace()
    size = len(solutionARP)
    solutionARP = np.setdiff1d(solutionARP, flightSchedule)
    verifySingletonSol(size, solutionARP, flightSchedule)

def updateMulti(flight2Cancel, airpCapCopy, solutionARP, aircraftSolList, configDic): #update airp. cap. ARP sol. and airc. sol. list
    #import pdb; pdb.set_trace()
    #return the flight list that can be cancelled
    if(len(flight2Cancel) == 0):
        return -1
    if(len(flight2Cancel[0]) == 0):
        return -1
    flight2Cancel = flight2Cancel[(flight2Cancel['altDepInt'] >= configDic['startInt']) & (flight2Cancel['altDepInt'] <= configDic['endInt'])]
    if(len(flight2Cancel[0]) == 0):
        return -1 #There are no flights that can be cancelled, the ARP solution is infeasible
    airc2Cancel = flight2Cancel[0]['aircraft'] #because it will be used to find the aircraft rotation
    rotationCancelAll = solutionARP[solutionARP['aircraft'] == airc2Cancel] #aircraft rotation
    
    airpCapRemove(rotationCancelAll, airpCapCopy) #remove the entire rotation from the airp. cap.
    rotationRemove(rotationCancelAll, solutionARP) #remove the entire rotation from the ARP solution
    aircraftSolList = list(set(aircraftSolList) - set(airc2Cancel)) #remove aircraft from the aircraftSolList 
    flight2Cancel[0]['cancelFlight'] = 1 #cancel the first flight from the list

def saveAirportCap(flightSchedule, airportCap): #update the airp. cap.
    for flight in flightSchedule[(flightSchedule['flight'] != '') & (flightSchedule['cancelFlight'] != 1)]:
        if flight['cancelFlight'] == 1:
            print("Airport capacity cancelled flight update saveAirportCap@solution.py")
            import pdb; pdb.set_trace()
            continue
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
        #verifyFlightRanges(flightRanges, rotation, 0)
        if delay == -1: #cancel the flight
            flight['cancelFlight'] = 1
        else:
            flight['altDepInt'] += delay
            flight['altArrInt'] += delay
        rotation[i] = flight #update the rotation
        i += 1

def updateItin(flightScheduleSA, itineraryDic):
    flight = {}
    for itinerary, flightSchedule in itineraryDic.items():
        fs = flightSchedule['flightSchedule'] #flights in the itinerary
        for f in fs: #loop through the itin. flight schedule to update the flights
            cancelFlight = flight.get(f['flight'], False) #get the cancel value or false
            if cancelFlight: #if the flight is in the flight dict.
                f['cancelFlight'] = cancelFlight #update itin. flight schedule
            else: #search, update add the flight to the flight dcit.
                cancelFlight = flightScheduleSA[flightScheduleSA['flight'] == f['flight']]['cancelFlight']
                if len(cancelFlight) == 0:
                    print("Un-existing flight: ", f['flight'])
                    pdb.set_trace()
                f['cancelFlight'] = cancelFlight[0] #update itin. flight schedule
                flight[f['flight']] = cancelFlight[0] #update the flight dict. 

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