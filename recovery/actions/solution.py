import pdb
import datetime
from recovery.dal.classesDtype import dtype as dt
from recovery.actions import feasibility
import numpy as np
import pandas as pd
from numpy import genfromtxt


def value(combo):
    noCancel = sum([t for t in combo if t == -1])
    totalDelay = sum([t for t in combo if t > 0])
    return noCancel, totalDelay, combo

def singletonRecovery(solutionARPDic, singletonList, airpCapCopy, configDic): #remove the flights form the airp. cap.
    solutionARP = []
    for rotation in solutionARPDic.values():
        solutionARP.append(rotation)
    solutionARP = np.concatenate(solutionARP).ravel()
    # if singletonList[0][0][0] == 'A318#125':
    #     pdb.set_trace()
    for singleton in singletonList: #remove the flights
        if singleton[1] == 'dep':
            startInt = 60 * int(singleton[0]['altDepInt']/60) #find the start of the time slot of the dep.
            endInt = startInt + 60
            origin = singleton[0]['origin']
            flight2Cancel = solutionARP[(solutionARP['origin'] == origin) & (solutionARP['cancelFlight'] == 0)] #find the origin of flight to be cancelled
            flight2CancelList = flight2Cancel[(flight2Cancel['altDepInt'] >= startInt) & (flight2Cancel['altDepInt'] < endInt) ]
            if len(flight2CancelList) == 0:
                # pdb.set_trace()
                flight2CancelList = flight2Cancel[(flight2Cancel['altDepInt'] < startInt) | (flight2Cancel['altDepInt'] > endInt) 
                    & (flight2Cancel['newFlight'] == 1) ]   
            airc2Cancel = updateMulti(flight2CancelList, airpCapCopy, solutionARP, configDic)
            if  airc2Cancel == -1:
                return -1
            return airc2Cancel

        if singleton[1] == 'arr':
            startInt = 60 *  int(singleton[0]['altArrInt']/60) #find the start of the time slot of the arr.
            endInt = startInt + 60
            destination = singleton[0]['destination']
            flight2Cancel = solutionARP[(solutionARP['destination'] == destination) & (solutionARP['cancelFlight'] == 0)] #find the origin of flight to be cancelled
            flight2CancelList = flight2Cancel[(flight2Cancel['altArrInt'] >= startInt) & (flight2Cancel['altArrInt'] < endInt) ]
            if len(flight2CancelList) == 0:
                pdb.set_trace()
                flight2CancelList = flight2Cancel[(flight2Cancel['altDepInt'] < startInt) | (flight2Cancel['altDepInt'] > endInt) 
                    & (flight2Cancel['newFlight'] == 1) ]  
            airc2Cancel = updateMulti(flight2CancelList, airpCapCopy, solutionARP, configDic)
            if  airc2Cancel == -1:
                return -1
            return airc2Cancel

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

def updateMulti(flight2Cancel, airpCapCopy, solutionARP, configDic): #update airp. cap. ARP sol. and airc. sol. list
    #import pdb; pdb.set_trace()
    #return the flight list that can be cancelled
    if(len(flight2Cancel) == 0):
        return -1
    if(len(flight2Cancel[0]) == 0):
        return -1
    #flight2Cancel = flight2Cancel[(flight2Cancel['altDepInt'] >= configDic['startInt']) & (flight2Cancel['altDepInt'] <= configDic['endInt'])]
    flight2Cancel = flight2Cancel[flight2Cancel['family'] != 'TranspCom']
    if(len(flight2Cancel) == 0):
        import pdb; pdb.set_trace()
        return -1 #There are no flights that can be cancelled, the ARP solution is infeasible
    if(len(flight2Cancel[0]) == 0):
        import pdb; pdb.set_trace()
        return -1 #There are no flights that can be cancelled, the ARP solution is infeasible
    
    airc2Cancel = flight2Cancel[0]['aircraft'] #because it will be used to find the aircraft rotation
    rotationCancelAll = solutionARP[solutionARP['aircraft'] == airc2Cancel] #aircraft rotation
    airpCapRemove(rotationCancelAll, airpCapCopy) #remove the entire rotation from the airp. cap.
    return airc2Cancel  #returns the airc. to cancel

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

def newPartialRotation(combo, rotation):
    for delay, flight in zip(combo, rotation):
        if delay == -1: #cancel the flight
            flight['cancelFlight'] = 1
        else:
            flight['altDepInt'] += delay 
            flight['altArrInt'] += delay
    return rotation

def partial(solutionARPDic):
    solutionARP = []
    for rotation in solutionARPDic.values(): #convert the sol. into no array
        solutionARP.append(rotation)
    fSNOTranspComSA = np.concatenate(solutionARP).ravel()
    return fSNOTranspComSA

def newRotation(combo, rotation): #create rotation based on combo
    feasibility.verifyNewRotation(combo, rotation[rotation['cancelFlight'] == 0]) #compare the size of the combo w/ rotation without disr.
    notCancel = rotation[rotation['cancelFlight'] == 0] #remove disr. flight
    for delay, flight in zip(combo, notCancel):
        #import pdb; pdb.set_trace()
        if delay == -1: #cancel the flight
            flight['cancelFlight'] = 1
        else:
            flight['altDepInt'] += delay 
            flight['altArrInt'] += delay
    rotation[rotation['cancelFlight'] == 0] = notCancel #update the rotation w/ the sol.
    return rotation

def export2CSV(solutionARP, dataSet, path = "solutions"): #export the ARP solution to CSV
    df = pd.DataFrame(solutionARP)
    df.to_csv(path + "\\" + dataSet + ".csv", index = False)
    
def importCSV(dataSet, path = "solutions"): #import the CSV to solutionARPDic
    df = pd.read_csv(path + "\\" + dataSet + ".csv")
    solutionARP = np.zeros(len(df), dtype = dt.dtypeFS)
    index = 0
    for rowDF in solutionARP:
        solutionARP[index] = tuple(df.iloc[index])
        index += 1
    return solutionARP

def updateItin(flightScheduleSA, itineraryDic, newFlightDic):
    flight = {}
    for itinerary, flightSchedule in itineraryDic.items():
        fs = flightSchedule['flightSchedule'] #flights in the itinerary
        for f in fs: #loop through the itin. flight schedule to update the flights
            newFlight = newFlightDic.get(f['flight'], False)
            try:
                if newFlight:
                    cancelFlight = flightScheduleSA[flightScheduleSA['flight'] == newFlight]['cancelFlight']
                    f['flight'] = newFlight
                    f['cancelFlight'] = cancelFlight[0] #update itin. flight schedule
                    continue
            except:
                continue
            cancelFlight = flight.get(f['flight'], False) #get the cancel value or false
            if cancelFlight: #if the flight is in the flight dict.
                f['cancelFlight'] = cancelFlight #update itin. flight schedule
            else: #search, update add the flight to the flight dcit.
                cancelFlight = flightScheduleSA[flightScheduleSA['flight'] == f['flight']]['cancelFlight']
                if len(cancelFlight) == 0:
                    print("Un-existing flight: ", f['flight'])
                    #pdb.set_trace()
                    continue
                f['cancelFlight'] = cancelFlight[0] #update itin. flight schedule
                flight[f['flight']] = cancelFlight[0] #update the flight dict. 
        
def export(flightScheduleSA, itineraryDic, minDate, path):
    sb = ""
    newCancel = flightScheduleSA[(flightScheduleSA['newFlight'] == 1) & (flightScheduleSA['cancelFlight'] == 1)] #new flights that were cancelled
    foundIndex = np.in1d(flightScheduleSA, newCancel).nonzero()[0] #indices of new flights that were cancelled
    flightScheduleSA = np.delete(flightScheduleSA, foundIndex) #delete new flights that were cancelled
    for fSA in flightScheduleSA:
        idFlight = fSA['flight'][:-8]

        date = datetime.datetime.strptime(fSA['flight'][len(idFlight):], dt.fmtDate) #convert to date
                            
        originFlight = fSA['origin']
        destinationFlight = fSA['destination']
        altDepInt = fSA['altDepInt']
        
        noDays = int(altDepInt / (60*24))
        noHours = int((altDepInt - noDays*60*24)/60)
        noMinutes = (altDepInt - noDays*60*24 - noHours*60)
        altDepDate = minDate + datetime.timedelta(days = noDays)
        altDepTime = datetime.datetime.strptime(str(noHours) + ":" + str(noMinutes), dt.fmtTime)

        altArrInt = fSA['altArrInt']
        noDays = int(altArrInt / (60*24))
        noHours = int((altArrInt - noDays*60*24)/60)
        noMinutes = (altArrInt - noDays*60*24 - noHours*60)
        altArrDate = minDate + datetime.timedelta(days = noDays)
        altArrTime = datetime.datetime.strptime(str(noHours) + ":" + str(noMinutes), dt.fmtTime)
        
        previous = fSA['previous']
        try:    
            if (altDepDate - date).days > 0:
                depNextDay = "+" + str((altDepDate - date).days) #fSA deleted
            else:
                depNextDay = ""

            if (altArrDate - date).days > 0:
                arrNextDay = "+" + str((altArrDate - date).days)
            else:
                arrNextDay = ""
        except:
            print("Exception finding export@solution.py")
            import pdb; pdb.set_trace()
        cancelFlight = fSA['cancelFlight']
        aircraft = fSA['aircraft']
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
        sb += str(itinerary) + " " + fs['typeItinerary'] + " " + str(fs['price']) + " " + str(fs['count'])
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

        sb += "\n"
    sb += "#"
    text_file = open(path+"\\sol_itineraries.csv", "w")
    text_file.write(sb)
    text_file.close()

def exportKPI(arpSolution, path, dataSet, deltaTime):

    import subprocess
    import os
    from datetime import datetime
    import pandas as pd
    import numpy as np
    import pdb
    from recovery.dal.classesDtype import pincer 
    delayFlight = arpSolution[arpSolution['altFlight'] == 0] #non disrupted flights
    delayFlight = delayFlight[delayFlight['cancelFlight'] == 0] #non cancelled flights
    totalDelay = sum(delayFlight['altDepInt'] - delayFlight['depInt']) #altDepInt - depInt
    cancelFlight = arpSolution[(arpSolution['cancelFlight'] == 1) & (arpSolution['altFlight'] != -1)]
    totalCancel = sum(cancelFlight['cancelFlight'])
    totalNewFlight = pincer.NEW_FLIGHT
    if pincer.NEW_FLIGHT != -1:
        newFlight = arpSolution[(arpSolution['newFlight'] == 1) & (arpSolution['cancelFlight'] == 0) & (arpSolution['taxiFlight'] == 0)] #new flight not cancelled not taxi flight
        totalNewFlight = sum(newFlight['newFlight'])
    totalTaxiFlight = pincer.TAXI_FLIGHT
    if pincer.TAXI_FLIGHT != -1:
        taxiFlight = arpSolution[(arpSolution['taxiFlight'] == 1) & (arpSolution['cancelFlight'] == 0)] #taxi flight not cancelled
        totalTaxiFlight = sum(taxiFlight['taxiFlight'])
    # pdb.set_trace()
    sizeLine = {}
    sizeLine['MAX_DELAY'] = []
    sizeLine['STEP_DOMAIN'] = []
    sizeLine['START_UPPER'] = []
    sizeLine['STEP_UPPER'] = []
    sizeLine['START_LOWER'] = []
    sizeLine['STEP_LOWER'] = []
    sizeLine['dateTime'] = []
    sizeLine['dataInstance'] = []
    sizeLine['checkAircraftBreakdownPeriod'] = []
    sizeLine['checkAircraftCapacity'] = []
    sizeLine['checkAircraftCreation'] = []
    sizeLine['checkAircraftSwap'] = []
    sizeLine['checkAirportCapacity'] = []
    sizeLine['checkCancellationofCreatedRotation'] = []
    sizeLine['checkFixedFlights'] = []
    sizeLine['checkFlight'] = []
    sizeLine['checkItinerary'] = []
    sizeLine['checkPassengerReac'] = []
    sizeLine['checkRotation'] = []
    sizeLine['costs'] = []
    sizeLine['deltaTime'] = []
    sizeLine['totalDelay'] = []
    sizeLine['totalCancel'] = []
    sizeLine['newFlight'] = []
    sizeLine['taxiFlight'] = []
    today = datetime.now().strftime("%Y%m%d_%H%M")

    os.chdir(path)
    os.system("./solutionChecker-static.i686-64")

    sizeLine['MAX_DELAY'].append(pincer.MAX_DELAY)
    sizeLine['STEP_DOMAIN'].append(pincer.STEP_DOMAIN)
    sizeLine['START_UPPER'].append(pincer.START_UPPER)
    sizeLine['STEP_UPPER'].append(pincer.STEP_UPPER)
    sizeLine['START_LOWER'].append(pincer.START_LOWER)
    sizeLine['STEP_LOWER'].append(pincer.STEP_LOWER)
    sizeLine['dateTime'].append(today)
    sizeLine['dataInstance'].append(dataSet)
    sizeLine['checkAircraftBreakdownPeriod'].append(os.path.getsize("./results/checkAircraftBreakdownPeriod.txt"))
    sizeLine['checkAircraftCapacity'].append(os.path.getsize("./results/checkAircraftCapacity.txt"))
    sizeLine['checkAircraftCreation'].append(os.path.getsize("./results/checkAircraftCreation.txt"))
    sizeLine['checkAircraftSwap'].append(os.path.getsize("./results/checkAircraftSwap.txt"))
    sizeLine['checkAirportCapacity'].append(os.path.getsize("./results/checkAirportCapacity.txt"))
    sizeLine['checkCancellationofCreatedRotation'].append(os.path.getsize("./results/checkCancellationofCreatedRotation.txt"))
    sizeLine['checkFixedFlights'].append(os.path.getsize("./results/checkFixedFlights.txt"))
    sizeLine['checkFlight'].append(os.path.getsize("./results/checkFlight.txt"))
    sizeLine['checkItinerary'].append(os.path.getsize("./results/checkItinerary.txt"))
    sizeLine['checkPassengerReac'].append(os.path.getsize("./results/checkPassengerReac.txt"))
    sizeLine['checkRotation'].append(os.path.getsize("./results/checkRotation.txt"))
    os.system("./costChecker-static.i686-64 > results/cost.txt")
    costs = np.genfromtxt('results/cost.txt', delimiter=':')
    sizeLine['costs'].append(costs[-1][1])
    sizeLine['deltaTime'].append(deltaTime)

    sizeLine['totalDelay'].append(totalDelay)
    sizeLine['totalCancel'].append(totalCancel)
    sizeLine['newFlight'].append(totalNewFlight)
    sizeLine['taxiFlight'].append(totalTaxiFlight)
    os.chdir("../../../")
    fileKPI = './results/kpiBat.csv'
    dataSetSizes = pd.DataFrame(sizeLine)
    try:
        dataSetSizes.to_csv(fileKPI, mode='a', index=False, header = False)
    except:
        import pdb; pdb.set_trace()
        dataSetSizes.to_csv(fileKPI, mode='a', index=False, header = False)