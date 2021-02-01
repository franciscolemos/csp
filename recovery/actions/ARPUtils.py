from recovery.dal.classesDtype import dtype as dt
from recovery.actions import solution
from recovery.actions import feasibility
from recovery.actions.funcsDate import int2DateTime
import numpy as np
import copy
import datetime
from recovery.dal.classesDtype import dtype as dt
class interval:
    def __init__(self, a, b): #"An interval of the form [a, b["
        self.a = a
        self.b = b

    def isInside(self, other):
        _i = any(other.a <= x < other.b for x in [self.a, self.b - 1])
        return _i

    def intersects(self, other):
        return self.isInside(other) or other.isInside(self)

    def findIntersection(self, others):
        for i, other in enumerate(others):
            if self.intersects(other):
                # if other.a >= self.a, offset is the difference
                # between other.a and self.a, otherwise self.a > other.a,
                # so the lower bound of self is inside the other interval,
                # so the offset is 0 away from the lower bound
                offset = other.a - self.a if other.a >= self.a else 0
                return i, offset

    def __add__(self, offset):
        return interval(self.a + offset, self.b + offset)

def newAircraftFlights(rotation, distSA, maxFlight, endInt, configDic): #get minDate, startInt:
    newFlights = rotation[rotation['flight'] == ''] #new flights
    rotationCancel = rotation[(rotation['altAirc'] == -1)] #flight cancelled by disr.
    #feasibility.verifyNewFlights(rotationCancel, newFlights) #check if no. of avail. slots equals 
    index = 0
    start = endInt + 1
    _flight = {}
    for cancelFlight, newFlight in zip(rotationCancel, newFlights): #loops through cancelled flights and new flights
        if index != 0: #to get the current the tt
            start = previousArr + cancelFlight['tt'] #it should be the next flight
        
        dist = distSA[(distSA['origin'] == cancelFlight['origin']) & (distSA['destination'] == cancelFlight['destination'])]['dist'][0]
        if start + dist > configDic['endInt']: #to prevent flight arriving after the end of recovery period
            continue #or break
        
        tmpFlight = cancelFlight['flight']
        newFlight['_flight'] = tmpFlight

        maxFlight += 1
        newFlight = cancelFlight
        newFlight['depInt'] = start #dep.
        newFlight['altDepInt'] = newFlight['depInt'] # alt dep.
        flightDate = int2DateTime(newFlight['depInt'], configDic['startDate']) #datetime when the broken period ends
        flightDate = flightDate.strftime('%d/%m/%y') #because the sol.checker has a bug
        flight = str(maxFlight) + flightDate
        _flight[tmpFlight] = flight
        newFlight['arrInt'] = newFlight['depInt'] + dist
        newFlight['altArrInt'] = newFlight['arrInt']
        newFlight['flight'] = flight
        newFlight['cancelFlight'] = 0
        newFlight['newFlight'] = 1
        newFlight['altAirc']  = 0
        newFlight['altFlight'] = 0
        newFlights[index] = newFlight
        previousArr = newFlight['arrInt'] #to get the arrival + tt for the next dep.
        if previousArr + newFlight['tt'] > configDic['endInt']:
            break #or continue
        index += 1

    rotation[rotation['flight'] == ''] = newFlights #update the rotation; rotation[rotation['flight'] == ''] != newFlights
    rotation = rotation[rotation['flight'] != '']
    #pdb.set_trace()
    return rotation, maxFlight, _flight

def newFlights(rotation, distSA, maxFlight, endInt, configDic):
    newFlights = rotation[rotation['flight'] == ''] #new flights
    rotationCancel = rotation[(rotation['altFlight'] == -1)] #flight cancelled by disr.
    startDep = 0 #offset
    rotation[rotation['flight'] == ''] = newFlights #update the rotation
    feasibility.verifyNewFlights(rotationCancel, newFlights) #check if no. of avail. slots equals 
    index = 0
    _flight = {}
    for cancelFlight, newFlight in zip(rotationCancel, newFlights): #loops through cancelled flights and new flights
        maxFlight += 1 #increment the maxFlight
        tmpFlight = cancelFlight['flight']
        newFlight['_flight'] = tmpFlight

        newFlight = cancelFlight
        dep = cancelFlight['depInt']
        # if dep < configDic['startInt']: #to prevent from c reating fixed flight (which of course are of hardly any use)
        #     dep = configDic['startInt']
        newFlight['depInt'] = dep - startDep + endInt + 1 #dep.
        newFlight['altDepInt'] = newFlight['depInt'] # alt dep.

        flightDate = int2DateTime(newFlight['depInt'], configDic['startDate']) #datetime when the broken period ends
        flightDate = flightDate.strftime('%d/%m/%y') #because the sol.checker has a bug
        flight = str(maxFlight) + flightDate
        _flight[tmpFlight] = flight
        dist = distSA[(distSA['origin'] == cancelFlight['origin']) & (distSA['destination'] == cancelFlight['destination'])]['dist'][0]
        newFlight['arrInt'] = newFlight['depInt'] + dist
        newFlight['altArrInt'] = newFlight['arrInt']
        newFlight['flight'] = flight
        newFlight['cancelFlight'] = 0
        newFlight['newFlight'] = 1
        newFlight['altAirc']  = 0
        newFlight['altFlight'] = 0
        newFlights[index] = newFlight
        index += 1
    rotation[rotation['flight'] == ''] = newFlights #update the rotation; rotation[rotation['flight'] == ''] != newFlights
    rotation = rotation[rotation['flight'] != '']
    return rotation, maxFlight, _flight  

def addMaint(aircraft, _rotationMaint):
    """
    Add aircraft maintenance to the flight schedule
    
    Args:
        rotationMaint (dtypeFS): Aircraft rotation with maintenance. Maintenance is particular flight where origin and destination are the same airport.
    """ 
    rotationMaint = np.zeros(1, dt.dtypeFS)
    rotationMaint['aircraft'][0] = aircraft
    rotationMaint['flight'][0] = 'm'
    rotationMaint['origin'][0] = _rotationMaint['origin'][0]
    rotationMaint['depInt'][0] = _rotationMaint['depInt'][0]
    rotationMaint['altDepInt'][0] = _rotationMaint['altDepInt'][0]
    rotationMaint['destination'][0] = _rotationMaint['destination'][0]
    rotationMaint['arrInt'][0] = _rotationMaint['arrInt'][0]
    rotationMaint['altArrInt'][0] = _rotationMaint['altArrInt'][0]
    return rotationMaint

def luAllContraints(combo, rotation, lIndex, uIndex):
    solution.newPartialRotation(combo, rotation[lIndex:uIndex]) # fin the new partial solution
    newRotation = rotation[:uIndex] #only the part until the upper index
    newRotation = newRotation[newRotation['cancelFlight'] == 0] #remove the cancelled flights
    newRotation = np.sort(newRotation[:uIndex], order = 'altDepInt') #order the rotation

    if len(feasibility.continuity(newRotation)) > 0: #only flights not cancelled in the copy
        return -1 #cont.
    if len(feasibility.TT(newRotation)) > 0: #only flights not cancelled in the copy
        return -1

def allConstraints(rotationOriginal, combo, index, movingFlights, fixedFlights, airpCapCopy, _rotationMaint, rotationMaint):
    rotation = copy.deepcopy(rotationOriginal) #keep a copy of the original because of new rotation
    solution.newRotation(combo, rotation[index:]) #add the combo to the rotation
    feasibility.verifyCombo(combo, rotation, index) #compare the size of combo w/ rotation
    feasibility.verifyRotation(rotation, movingFlights, fixedFlights, index) #compare rotation size w/ ...
    rotationCopy = copy.deepcopy(rotation[rotation['cancelFlight'] != 1]) #only flights not cancelled in the copy
    #add the initial position to the rotation
    rotationCopy = np.sort(rotationCopy, order = 'altDepInt')
    
    if len(feasibility.continuity(rotationCopy)) > 0: #only flights not cancelled in the copy
        return -1 #cont.
    if len(feasibility.TT(rotationCopy)) > 0: #only flights not cancelled in the copy
        return -1

    if ((len(feasibility.dep(rotationCopy, airpCapCopy)) > 0) |
         (len(feasibility.arr(rotationCopy, airpCapCopy)) > 0)):
        import pdb; pdb.set_trace()
        return -2                    
    if len(rotation[(rotation['previous'] != '0') & (rotation['previous'] != '')]) > 0: # because previous flight exist
        if len(feasibility.previous(rotation)) > 0:
            return -1

    if (len(_rotationMaint) > 0):
        rotationMaintConcat = np.concatenate((rotationCopy, rotationMaint))
        rotationMaintConcat = np.sort(rotationMaintConcat, order = 'altDepInt')
        infMaintList = feasibility.maint(rotationMaintConcat)
        if len(infMaintList) > 0:
            return -1

def wipRecover2(aircraft, altAircraftDic, distSA, originAirport, solRot, airportDic, configDic, maxFlight): #wrong init. pos. recovery
    #loop through solRot to try find a taxi flight or find the airc. origin airp.
    altSI = -1
    altEI = -1
    if aircraft in altAircraftDic:
        altSI = altAircraftDic[aircraft]['startInt'] #start of airc. broken period
        altEI = altAircraftDic[aircraft]['endInt'] #end of of airc. broken period  
    for sr in solRot:
        if sr['origin'] == originAirport:
            print("Airc. Origin airp = Flight origin")
            return solRot, maxFlight
                
        distInitRot = distSA[(distSA['origin'] == originAirport) & (distSA['destination'] == sr['origin'])] #dist. for airc. origin to solRot flight
        distInitRot = distInitRot['dist'][0] #dist. for airc. origin to solRot flight
        
        originSlots = airportDic[originAirport] #find airp. time slot for dep. @origin
        originSlots = originSlots[originSlots['capDep'] > originSlots['noDep']] #find airp. time slot for dep. @origin w/ avail. dep. cap.
        originSlotsUpper =  originSlots[originSlots['endInt'] > (sr['altDepInt'] - distInitRot - sr['tt'])] #upper slots dep. of next flight - dist. - tt
        originSlotsLower =  np.setdiff1d(originSlots, originSlotsUpper)

        if (altSI >= 0) & (altEI >= 0): #if there is a airc. break. period
            originSlotsAircBreakDown = originSlotsLower[(originSlotsLower['startInt'] >= altSI) 
                                        & (originSlotsLower['startInt'] < altEI)] #slots inside  the aircraft
            _originSlots = np.setdiff1d(originSlotsLower, originSlotsAircBreakDown)
        else:
            _originSlots = originSlotsLower
        
        if len(_originSlots) == 0:
            print("No available taxi flight")
            sr['cancelFlight'] = 1
            continue
        
        #find airp. time slot for arr. @dest.
        destSlots = airportDic[sr['origin']]
        destSlots = destSlots[destSlots['capArr'] > destSlots['noArr']]
        destSlotsUpper = destSlots[destSlots['endInt'] > (sr['altDepInt'] - sr['tt'])]
        destSlotsLower = np.setdiff1d(destSlots, destSlotsUpper)

        if (altSI >= 0) & (altEI >= 0): #if there is a airc. break. period
            destSlotsAircBreakDown = destSlotsLower[(destSlotsLower['startInt'] >= altSI) 
                                        & (destSlotsLower['startInt'] < altEI)] #slots inside  the aircraft
            _destSlots = np.setdiff1d(destSlotsLower, destSlotsAircBreakDown)
        else:
            _destSlots = destSlotsLower

        if len(_destSlots) == 0:
            print("No available taxi flight")
            sr['cancelFlight'] = 1
            continue

        otherIntervals = []
        i = -1; offset = -1
        for x in _destSlots: #instatiate dest. slots
            otherIntervals.append(interval(x['startInt'], x['endInt']))
        for os in _originSlots:
            obj1 = interval(os['startInt'], os['endInt']) + distInitRot #start end dist
            try: 
                i, offset = obj1.findIntersection(otherIntervals)
                print(i, offset, os)
                break
            except:
                continue
        if i != -1: #check if there is a taxi flight
            taxiFlight = np.zeros(1, dtype = dt.dtypeFS)
            taxiFlight[0] = copy.deepcopy(sr)

            taxiFlight['origin'] = originAirport
            taxiFlight['depInt'] = os['startInt'] + offset #dep.
            taxiFlight['altDepInt'] = taxiFlight['depInt'] # alt dep.

            flightDate = int2DateTime(taxiFlight['depInt'][0], configDic['startDate']) #datetime when the broken period ends
            flightDate = flightDate.strftime('%d/%m/%y') #because the sol.checker has a bug
            maxFlight += 1
            flight = str(maxFlight) + flightDate

            taxiFlight['destination'][0] = sr['origin'] #origin of the first flight in sol. rot.
            taxiFlight['arrInt'] = taxiFlight['depInt'][0] + distInitRot
            taxiFlight['altArrInt'] = taxiFlight['arrInt'][0]
            taxiFlight['flight'] = flight
            taxiFlight['cancelFlight'] = 0
            taxiFlight['newFlight'] = 1
            taxiFlight['_flight'] = '-1'
            taxiFlight['altAirc']  = 0
            taxiFlight['altFlight'] = 0
            print("Taxi flight found!!!")
            solRot = np.concatenate((solRot, taxiFlight))
            return solRot, maxFlight
        ################################## start optional else ############################
        # it's optional because the search procedure becomes less expensive since the airp.
        # cap slots are filled w/ inf. solutions;
        # the solution can be recovered in the end; 
        else: #cancel the rotation
            print("No available taxi flight")
            sr['cancelFlight'] = 1
        ################################## en optional else ################################
    return solRot, maxFlight

def convertFlight(rotation, minDate):
    for flight in rotation:
        date = datetime.datetime.strptime(flight['flight'][-8:], dt.fmtDate) #convert to date
        altDepInt = flight['altDepInt']
        noDays = int(altDepInt / (60*24))
        altDepDate = minDate + datetime.timedelta(days = noDays)
        daysDiff = (altDepDate - date).days
        if daysDiff> 0:
            newFlightDate = date + datetime.timedelta(days = 1) #add the no. of days to the flight's date
            newFlightDateString = newFlightDate.strftime(dt.fmtDate) #format the flight's date to string
            flight['flight'] = flight['flight'][:-8] + newFlightDateString #update the flight
            flight['altDepInt'] = flight['altDepInt'] - daysDiff * 60 * 24 #update the dep.
            flight['depInt'] = flight['altDepInt']
            flight['altArrInt'] = flight['altArrInt'] - daysDiff * 60 * 24 #update the arr.
            flight['arrInt'] = flight['altArrInt']
            newFlight = copy.deepcopy(flight)
            flight = newFlight
    return rotation