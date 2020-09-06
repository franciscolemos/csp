#this module aims at helping finding parts of the solution e.g. taxi flights
from recovery.dal.classesDtype import dtype as dt
import numpy as np
from recovery.actions.funcsDate import int2DateTime
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

def wipRecover(distSA, originAirport, solRot, airportDic, rotationOriginal, configDic, maxFlight): #wrong init. pos. recovery
    distInitRot = distSA[(distSA['origin'] == originAirport) & (distSA['destination'] == solRot[0]['origin'])]
    distInitRot = distInitRot['dist'][0]
    #find airp. time slot for dep. @origin
    originSlots = airportDic[originAirport]
    originSlots = originSlots[originSlots['endInt'] < (solRot[0]['altDepInt'] - distInitRot)]
    originSlots = originSlots[originSlots['capDep'] > originSlots['noDep']]
    #find airp. time slot for arr. @dest.
    destSlots = airportDic[solRot[0]['origin']]
    destSlots = destSlots[destSlots['startInt'] < solRot[0]['altDepInt']]
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
        taxiFlight[0] = copy.deepcopy(solRot[0])

        taxiFlight['origin'] = originAirport
        taxiFlight['depInt'] = os['startInt'] + offset #dep.
        taxiFlight['altDepInt'] = taxiFlight['depInt'] # alt dep.

        flightDate = int2DateTime(taxiFlight['depInt'][0], configDic['startDate']) #datetime when the broken period ends
        flightDate = flightDate.strftime('%d/%m/%y') #because the sol.checker has a bug
        maxFlight += 1
        flight = str(maxFlight) + flightDate

        taxiFlight['destination'][0] = solRot[0]['origin'] #origin of the first flight in sol. rot.
        taxiFlight['arrInt'] = taxiFlight['depInt'][0] + distInitRot
        taxiFlight['altArrInt'] = taxiFlight['arrInt'][0]
        taxiFlight['flight'] = flight
        taxiFlight['cancelFlight'] = 0
        taxiFlight['newFlight'] = 1
        taxiFlight['altAirc']  = 0
        taxiFlight['altFlight'] = 0
        rotationOriginal = np.concatenate((rotationOriginal, taxiFlight))
    ################################## start optional else ############################
    # it's optional because the search procedure becomes less expensive since the airp.
    # cap slots are filled w/ inf. solutions;
    # the solution can be recovered in the end; 
    else: #cancel the rotation
        print("No available taxi flight")
        for sr in solRot:
            if sr['origin'] != originAirport:
                sr['cancelFlight'] = 1
            else:
                break
        rotationOriginal[rotationOriginal['cancelFlight'] == 0] = solRot
    ################################## en optional else ################################
    return rotationOriginal, maxFlight

def wipRecover2(distSA, originAirport, solRot, airportDic, rotationOriginal, configDic, maxFlight): #wrong init. pos. recovery
    
    #loo through solRot to try find a taxi flight or find the airc. origin airp.
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