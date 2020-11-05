import datetime
from recovery.dal.classesDtype import dtype as dt
from recovery.actions import solution
import time
import copy
from numpy import array
import numpy as np
from pprint import pprint
import pandas as pd
import pdb

def previous(flightSchedule):
    previousList = flightSchedule[(flightSchedule['previous'] != '0') & (flightSchedule['previous'] != '')] #because of created flights
    for flight in previousList: #flights w/ previous
        date = flight['flight'][-8:] #get the date
        #import pdb; pdb.set_trace()
        previousFlight = flight['previous'] + date #previous flight
        cancelFlight = flightSchedule[flightSchedule['flight'] == previousFlight]['cancelFlight']
        if (cancelFlight == 1) & (flight['cancelFlight'] != 1):
            return [-1] #next flight not cancelled
    return [] #feasible

def continuity(flightSchedule):
    index =  np.where(flightSchedule['destination'][:-1] != flightSchedule['origin'][1:]) # this matrix will be 1 row smaller 
    if len(index) > 2:
        import pdb; pdb.set_trace()
    return np.asarray(index).flatten() + 1 #the problem is on the next row in the original rotation

def TT(flightSchedule):
    index =  np.where(flightSchedule['altDepInt'][1:] - flightSchedule['altArrInt'][:-1] < flightSchedule['tt'][1:])
    if len(index) > 2:
        import pdb; pdb.set_trace()
    return np.asarray(index).flatten() + 1 #the problem is on the next row in the original rotation

def maint(flightSchedule):
    
    maintStart = flightSchedule[flightSchedule['flight'] == 'm']['altDepInt'][0]
    maintEnd = flightSchedule[flightSchedule['flight'] == 'm']['altArrInt'][0]
    maintOrigin = flightSchedule[flightSchedule['flight'] == 'm']['origin'][0]
    flightBeforeMaint = flightSchedule[(flightSchedule['altDepInt'] <= maintStart) & (flightSchedule['flight'] != 'm')]
    if len(flightBeforeMaint) > 0:
        flightBeforeMaint = flightBeforeMaint[-1]
    else:
        return [-1]
    

    #flights arr. after maint. start
    if (maintStart - flightBeforeMaint['altArrInt'] < 0) | (maintOrigin != flightBeforeMaint['destination']):
        index = np.where(flightSchedule['flight'] == flightBeforeMaint['flight'])
        return np.asarray(index).flatten()
    
    #flights departing during maint.
    flightDuringMaint = flightSchedule[(flightSchedule['altDepInt'] >= maintStart) & (flightSchedule['flight'] != 'm')
        & (flightSchedule['altDepInt'] <= maintEnd)]
    if len(flightDuringMaint) > 0:
        index = np.where(flightSchedule['flight']  == flightDuringMaint['flight'][0] )
        return np.asarray(index).flatten()

    return []
#dep. airp. cap.
def dep(flightSchedule, airportDic, delta = 1):
    flightDepList = []
    flightIndex = 0
    
    for flight in flightSchedule[flightSchedule['flight'] != '']:
        try:
            if flight['cancelFlight'] == 1: continue
            index = int(flight['altDepInt'] / 60)
            noDep = airportDic[flight['origin']][index]['noDep']
            capDep = airportDic[flight['origin']][index]['capDep']
            if noDep + delta > capDep:
                flightDepList.append(flightIndex)
                #import pdb; pdb.set_trace()
            flightIndex += 1
        except:
            print("index is out of bounds")
            import pdb; pdb.set_trace()
    return flightDepList 
#arr. airp. cap.
def arr(flightSchedule, airportDic, delta = 1):
    flightArrList = []
    flightIndex = 0
    
    for flight in flightSchedule[flightSchedule['flight'] != '']:
        if flight['cancelFlight'] == 1: continue
        index = int(flight['altArrInt'] / 60)
        noArr = airportDic[flight['destination']][index]['noArr']
        capArr = airportDic[flight['destination']][index]['capArr']
        if noArr + delta > capArr:
            flightArrList.append(flightIndex)
            #import pdb; pdb.set_trace()
        flightIndex += 1
    
    return flightArrList

def airportCap(airportDic):
    infeasCap = []
    for airport, capArr in airportDic.items():
        for cap in capArr:
            if cap['noArr'] > cap['capArr']:
                print('No. or arr.', cap['noArr'],' is bigger that arr. cap.', cap['capArr'], 'for airport', airport)
                infeasCap.append([airport, cap, 'arr.'])
            if cap['noDep'] > cap['capDep']:
                print('No. or dep.', cap['noDep'],' is bigger that dep. cap.', cap['capDep'], 'for airport', airport)
                infeasCap.append([airport, cap, 'dep.'])
    return infeasCap  

def initialPosition(flightSchedule, aircOrigin):
    if flightSchedule['origin'] != aircOrigin:
        return [0]
    return []

def verifyNullFlights(rotation): #verify if there are any null flights
    if(len(rotation[rotation['flight'] == '']) > 0):
        print("Null flights in the rotation verify NullFlights@solution.py")
        pdb.set_trace()

def verifyNewFlights(rotationCancel, newFlights):
    if len(rotationCancel) != len(newFlights):
        print("No. cancelled flights diff. of no. new flights verifyNewFlights@solution.py")
        pdb.set_trace()

def verifyFlightRanges(flightRanges, rotation, index):
    sizeRotation = len(rotation[index:][rotation[index:]['cancelFlight'] != 1]) #only consider flights not cancelled
    if len(flightRanges) != sizeRotation:
        print("No. ranges diff. remaining flights verifyFlightRanges@solution.py")
        pdb.set_trace()

def verifyCombo(combo, rotation, index):
    rotationDisr = rotation[index:]
    rotationDisr = rotationDisr[(rotationDisr['altFlight'] != -1) & (rotationDisr['altAirc'] != -1)]
    sizeRotation = len(rotationDisr) #only consider flights not disr.
    if len(combo) != sizeRotation:
        print("Combo size is diff. from remaining rotation verifyCombo@solution.py")
        pdb.set_trace()

def verifyRotation(rotation, movingFlights, fixedFlights, index):
    if len(rotation) != len(rotation[:index]) + len(movingFlights) + len(fixedFlights):
        print("Diff. in rotation length verifyRotation@solution.py")
        pdb.set_trace()

def verifySingletonSol(size, solutionARP, flightSchedule):
    if size != len(solutionARP) + len(flightSchedule):
        print("Diff. in solutionARP length verifySingletonSol@solution.py")
        pdb.set_trace()

def verifyNewRotation(combo, rotation):
    if len(combo) != len(rotation):
        print("Diff. in size between rotation and combo")
        pdb.set_trace()