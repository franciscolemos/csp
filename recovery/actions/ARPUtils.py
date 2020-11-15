from recovery.dal.classesDtype import dtype as dt
from recovery.actions import solution
from recovery.actions import feasibility
from recovery.actions.funcsDate import int2DateTime
import numpy as np
import copy
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
    startDep = rotationCancel[0]['depInt'] #offset
    feasibility.verifyNewFlights(rotationCancel, newFlights) #check if no. of avail. slots equals 
    index = 0
    start = endInt + 1
    for cancelFlight, newFlight in zip(rotationCancel, newFlights): #loops through cancelled flights and new flights
        if index != 0: #to get the current the tt
            start = previousArr + cancelFlight['tt'] #it should be the next flight
        
        dist = distSA[(distSA['origin'] == cancelFlight['origin']) & (distSA['destination'] == cancelFlight['destination'])]['dist'][0]
        if start + dist > configDic['endInt']: #to prevent flight arriving after the end of recovery period
            continue #or break

        maxFlight += 1
        newFlight = cancelFlight
        newFlight['depInt'] = start #dep.
        newFlight['altDepInt'] = newFlight['depInt'] # alt dep.
        flightDate = int2DateTime(newFlight['depInt'], configDic['startDate']) #datetime when the broken period ends
        flightDate = flightDate.strftime('%d/%m/%y') #because the sol.checker has a bug
        flight = str(maxFlight) + flightDate
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
    return rotation, maxFlight

def newFlights(rotation, distSA, maxFlight, endInt, configDic):
    newFlights = rotation[rotation['flight'] == ''] #new flights
    rotationCancel = rotation[(rotation['altFlight'] == -1)] #flight cancelled by disr.
    startDep = 0 #offset
    rotation[rotation['flight'] == ''] = newFlights #update the rotation
    feasibility.verifyNewFlights(rotationCancel, newFlights) #check if no. of avail. slots equals 
    index = 0
    for cancelFlight, newFlight in zip(rotationCancel, newFlights): #loops through cancelled flights and new flights
        maxFlight += 1 #increment the maxFlight
        newFlight = cancelFlight
        dep = cancelFlight['depInt']
        # if dep < configDic['startInt']: #to prevent from c reating fixed flight (which of course are of hardly any use)
        #     dep = configDic['startInt']
        newFlight['depInt'] = dep - startDep + endInt + 1 #dep.
        newFlight['altDepInt'] = newFlight['depInt'] # alt dep.

        flightDate = int2DateTime(newFlight['depInt'], configDic['startDate']) #datetime when the broken period ends
        flightDate = flightDate.strftime('%d/%m/%y') #because the sol.checker has a bug
        flight = str(maxFlight) + flightDate
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
    return rotation, maxFlight   

def cancelLoop(rotation, flightRanges): #cancel loop flight to find feas. sol.
    origin = rotation[0]['origin'] #origin 
    rotation[0]['cancelFlight'] = 1 #cancel the first infea. flight
    combo = [0] * len(flightRanges)
    combo[0] = -1
    for index, flight in enumerate(rotation[1:], 1): #start at second flight
        if flightRanges[flight['flight']][0] == -1: #the first value is cancel
            if (flight['origin'] != origin):
                flight['cancelFlight'] = 1 #cancel the flight
                combo[index] = -1 #add cancel. to combo
            else:
                return tuple(combo)
        else: #singleton
            print("Singleton found")
            import pdb; pdb.set_trace()
            return False


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

def wipRecover2(distSA, originAirport, solRot, airportDic, rotationOriginal, configDic, maxFlight): #wrong init. pos. recovery
    #loop through solRot to try find a taxi flight or find the airc. origin airp.
    for sr in solRot:
        if sr['origin'] == originAirport:
            print("Airc. Origin airp = Flight origin")
            #import pdb; pdb.set_trace()
            rotationOriginal[rotationOriginal['cancelFlight'] == 0] = solRot
            return rotationOriginal, maxFlight
                
        distInitRot = distSA[(distSA['origin'] == originAirport) & (distSA['destination'] == sr['origin'])]
        distInitRot = distInitRot['dist'][0] #dist. for airc. origin to solRot flight
        #find airp. time slot for dep. @origin
        originSlots = airportDic[originAirport]
        originSlots = originSlots[originSlots['endInt'] < (sr['altDepInt'] - distInitRot)]
        originSlots = originSlots[originSlots['capDep'] > originSlots['noDep']]
        #find airp. time slot for arr. @dest.
        destSlots = airportDic[sr['origin']]
        destSlots = destSlots[destSlots['startInt'] < sr['altDepInt']]
        destSlots = destSlots[destSlots['capArr'] > destSlots['noArr']]

        otherIntervals = []
        i = -1; offset = -1
        for x in destSlots: #instatiate dest. slots
            otherIntervals.append(interval(x['startInt'], x['endInt']))
        for os in originSlots:
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
            taxiFlight['altAirc']  = 0
            taxiFlight['altFlight'] = 0
            print("Taxi flight found!!!")
            #import pdb; pdb.set_trace()
            rotationOriginal[rotationOriginal['cancelFlight'] == 0] = solRot
            rotationOriginal = np.concatenate((rotationOriginal, taxiFlight))
            return rotationOriginal, maxFlight
        ################################## start optional else ############################
        # it's optional because the search procedure becomes less expensive since the airp.
        # cap slots are filled w/ inf. solutions;
        # the solution can be recovered in the end; 
        else: #cancel the rotation
            print("No available taxi flight")
            #import pdb; pdb.set_trace()
            sr['cancelFlight'] = 1
        ################################## en optional else ################################
    
    import pdb; pdb.set_trace()
    rotationOriginal[rotationOriginal['cancelFlight'] == 0] = solRot
    return rotationOriginal, maxFlight