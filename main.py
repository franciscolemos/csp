# Using a Python dictionary to act as an adjacency list
import pdb
import numpy as np
from recovery.repositories import *
import recovery.actions.funcsDate as fD
from recovery.actions import scenario
from datetime import datetime
from recovery.actions import domains #domains is updated at each iteration
import recovery.actions.dfs2 as aD #it is not necessary to import the entire package, only some modules
from recovery.actions import feasibility
from recovery.actions import solution
from recovery.actions import cost
import random
import copy
import time
from itertools import product
from recovery.dal.classesDtype import dtype as dt
import pandas as pd

class ARP:
    def __init__(self, path):
        self.solution = {}
        self.visited = [] # Array to keep track of visited nodes.
        self.criticalFlight = []
        self.fixedFlights = []
        self.movingFlights = []
        self.flightRotationDic = readRotation.readRotation(path, "rotations.csv").read2FlightRotationDic() #{flightDate:aircraft}
        self.minDate = self.flightRotationDic['minDate']
        maxDate = self.flightRotationDic['maxDate']
        self.configDic = readConfig.readConfig(path, "config.csv", self.minDate).read2Dic()
        self.aircraftRotationDic = readRotation.readRotation(path, "rotations.csv").read2AircraftRotationDic() #{aircraft:flightSchedule}
        self.flightDic = readFlights.readFlights(path, "flights.csv").read2Dic()  
        self.aircraftDic = readAircrafts.readAircrafts(path, "aircraft.csv", self.minDate).read2Dic()
        self.altAircraftDic = readAltAircraft.readAltAircraft(path, "alt_aircraft.csv", self.minDate).read2Dic()
        self.altAirportSA = readAltAirports.readAltAirport(path, "alt_airports.csv", self.minDate).read2SA() #atttrib. of SA
        self.altFlightDic = readAltFlights.readAltFlights(path, "alt_flights.csv").read2Dic()
        self.distSA = readDist.readDist(path, "dist.csv").read2SA()
        i = schedules.initialize(self.aircraftRotationDic, self.altAircraftDic, self.altFlightDic, 
            self.aircraftDic, self.flightDic, path, self.minDate)
        i.aircraftSchedule() #included flight and aircr. disr. and, maint. {aircraft:flightSA}
        self.aircraftScheduleDic = i.aircraftScheduleDic #1 aircraft to n flights
        i.flightSchedule()
        self.flightScheduleSA = i.flightScheduleSA #all the flights + room to un-cancel flights for airport cap. purpose
        self.itineraryDic = readItineraries.readItineraries(path,"itineraries.csv").read2Dic()
        #determine the planning horizon
        endDateTime = datetime.combine(datetime.date(self.configDic['endDate']),
            datetime.time(self.configDic['endTime']))
        if maxDate < endDateTime:
            self.flightRotationDic['maxDate'] = endDateTime 
            maxDate = endDateTime 
        noDays = fD.dateDiffDays(maxDate, self.minDate) + 1 # + 1 day for arr. next()
        self.fSNOTranspComSA = self.flightScheduleSA[self.flightScheduleSA['family'] != "TranspCom"]
        self.airportOriginaltDic = readAirports.readAirports(path, "airports.csv", noDays, self.altAirportSA, []).read2Dic() #does not include noDep/noArr 

        scenario.echo(len(self.flightDic), len(self.aircraftDic), len(self.airportOriginaltDic),
                    len(self.itineraryDic),
                    #-1,
                    len(self.altFlightDic), len(self.altAircraftDic),
                    len(self.altAirportSA), noDays - 1)

        self.domainFlights = domains.flights(self.configDic)

        self.solutionARP = []

    def initialize(self, aircraft, airportDic, delta = 1, saveAirportCap = True): #check if the roation is feasible

        rotationOriginal = self.fSNOTranspComSA[self.fSNOTranspComSA['aircraft'] == aircraft]
        rotationOriginal = rotationOriginal[rotationOriginal['flight']!= ''] #remove created flights
        rotation = rotationOriginal[(rotationOriginal['cancelFlight'] == 0) ] #only flying flights
        rotation = np.sort(rotation, order = 'altDepInt') #sort ascending
        #check rotation feasibility
        infContList = feasibility.continuity(rotation) #cont.
        infTTList = feasibility.TT(rotation) #TT
        
        rotationMaint = np.sort(self.aircraftScheduleDic[aircraft], order = 'altDepInt') #select the aircr. and sort the rotation
        self._rotationMaint = rotationMaint[rotationMaint['flight'] == 'm'] #find if the rotation has maint. scheduled
        infMaintList = []
        if len(self._rotationMaint) > 0:
            infMaintList = feasibility.maint(rotationMaint) # find if maint. const. is infeas.
        
        infDepList = feasibility.dep(rotation, airportDic, delta) #airp. dep. cap.
        infArrList = feasibility.arr(rotation, airportDic, delta) #airp. arr. cap.
        try:
            feasible = len(infContList) + len(infTTList) + len(infMaintList) + len(infDepList) + len(infArrList)

            #print("feasible:", len(infContList), len(infTTList), len(infMaintList), len(infDepList), len(infArrList))
            if feasible == 0:
                if saveAirportCap:
                    self.solutionARP.append(rotationOriginal) #save the feasible rotation w/ cancelled flights
                    solution.saveAirportCap(rotation, airportDic) #update the airp. cap. only w/ cancelFlight == 0
                return -1, [] #for repair to determine if the problem is dep. or arr.
            else:
                
                    #print("infeasiblities:", infContList, infTTList, infMaintList, infDepList, infArrList)
                    index = min(np.concatenate((infContList, infTTList, infMaintList, infDepList, infArrList), axis = None)) #find tme min. index; wgere the problem begins
                    return int(index), rotationOriginal #because it has to include the aircraft to export the solution
        except Exception as e:
            print("Exception initialize:", e)
            import pdb; pdb.set_trace()
        #visualize the graphs
    
    def addMaint(self, aircraft):
        rotationMaint = np.zeros(1, dt.dtypeFS)
        rotationMaint['aircraft'][0] = aircraft
        rotationMaint['flight'][0] = 'm'
        rotationMaint['origin'][0] = self._rotationMaint['origin'][0]
        rotationMaint['depInt'][0] = self._rotationMaint['depInt'][0]
        rotationMaint['altDepInt'][0] = self._rotationMaint['altDepInt'][0]
        rotationMaint['destination'][0] = self._rotationMaint['destination'][0]
        rotationMaint['arrInt'][0] = self._rotationMaint['arrInt'][0]
        rotationMaint['altArrInt'][0] = self._rotationMaint['altArrInt'][0]
        return rotationMaint

    def loopAircraftList(self, aircraftList, airportDic):
        import copy; aircraftTmpList = copy.deepcopy(aircraftList)
        solutionKpiExport = []
        noFlights = 0
        noCancelledFlights = 0
        aircraftSolList = [] #list of aircraft that have a feasibe rotation
        _noCombos = 0.1 #order of magnitude for the no. of combos
        while len(aircraftSolList) != len(aircraftList): #verify if the lists have the same size
            remainAirc = len(list(set(aircraftList) - set(aircraftSolList)))
            for aircraft in aircraftTmpList: #iterate through the aircraft list
                print(aircraft)
                if('TranspCom' in aircraft): #immediatly add the surface transport
                    aircraftSolList.append(aircraft)
                    rotation = self.flightScheduleSA[self.flightScheduleSA['aircraft'] == aircraft]
                    self.solutionARP.append(rotation)
                    continue
                index, rotationOriginal  = self.initialize(aircraft, airportDic) #save a feasible rotation or return the index of inf.
                if(index != -1): #search the solution
                    #import pdb; pdb.set_trace()
                    rotation = copy.deepcopy(rotationOriginal) #copy the original rotation 
                    fixedFlights = self.domainFlights.fixed(rotation[index:]) #find the fixed flights: disrupted and outside RTW
                    if fixedFlights.size == 0: #if there are no fixed flights
                        movingFlights = rotation[index:]
                    else:#if there are fixed flights remove them from the remianing rotation
                        movingFlights = np.setdiff1d(rotation[index:], fixedFlights) 
                    airpCapCopy = copy.deepcopy(airportDic) #copy the airp. cap. solution
                     #flight ranges and combinations only for moving flight after disruption index with updated airp. cap. for fixed flights
                    flightRanges, noCombos, singletonList = self.domainFlights.ranges(rotation[index:], airpCapCopy, _noCombos)
                    
                    if len(singletonList) >= 1: #[(flight, 'dep')]
                        #import pdb; pdb.set_trace()
                        if solution.singletonRecovery(self.solutionARP, singletonList, airpCapCopy, self.configDic) == -1:
                            return 1, aircraft, _noCombos, len(aircraftSolList),  noFlights, noCancelledFlights 
                    
                    if noCombos == -1: #excssive no. combos
                        #print(aircraft, _noCombos, "Excessive", noCombos, remainAirc, len(aircraftSolList))
                        continue #resume next aircraft
                    
                    start = time.time()

                    solution.verifyFlightRanges(flightRanges, rotation, index) #check if flight ranges has the same size of rotation[index:]
                    if len(self._rotationMaint) > 0:
                        rotationMaint = self.addMaint(aircraft) #creates the maint to be later added to the rotation
                    flightCombinations = product(*flightRanges.values()) #find all the combinations
                    solutionValue = [] #initializes the solution value for later appraisal

                    for combo in flightCombinations: #loop through the possible combinations
                        rotation = copy.deepcopy(rotationOriginal) #keep a copy of the original because of new rotation
                        solution.newRotation(combo, rotation[index:]) #add the combo to the rotation
                        solution.verifyCombo(combo, rotation, index) #compare the size of combo w/ rotation
                        solution.verifyRotation(rotation, movingFlights, fixedFlights, index) #compare rotation size w/ ...
                        rotationCopy = copy.deepcopy(rotation[rotation['cancelFlight'] != 1]) #only flights not cancelled in the copy
                        rotationCopy = np.sort(rotationCopy, order = 'altDepInt')
                        
                        if len(feasibility.continuity(rotationCopy)) > 0:#only flights not cancelled in the copy
                            continue #cont.
                        if len(feasibility.TT(rotationCopy)) > 0:#only flights not cancelled in the copy
                            continue


                        if (len(feasibility.dep(rotationCopy, airpCapCopy)) > 0) | (len(feasibility.arr(rotationCopy, airpCapCopy)) > 0):
                            import pdb; pdb.set_trace()
                            break                     
                            #return 0, aircraft, _noCombos, len(aircraftSolList),  noFlights, noCancelledFlights 
                        if len(rotation[(rotation['previous'] != '0') & (rotation['previous'] != '')]) > 0: # because previous flight exist
                            if len(feasibility.previous(rotation)) > 0:
                                continue

                        if (len(self._rotationMaint) > 0):
                            rotationMaintConcat = np.concatenate((rotationCopy, rotationMaint))
                            rotationMaintConcat = np.sort(rotationMaintConcat, order = 'altDepInt')
                            infMaintList = feasibility.maint(rotationMaintConcat)
                            if len(infMaintList) > 0:
                                continue

                        solutionValue.append(solution.value(combo))
                    try:
                        df = pd.DataFrame(solutionValue)
                        df = df.sort_values(by=[0, 1], ascending=[False, True])
                    except:
                        import pdb; pdb.set_trace()
                        return 1, aircraft, _noCombos, len(aircraftSolList),  noFlights, noCancelledFlights 
                        #import pdb; pdb.set_trace()
                    solution.newRotation(df.iloc[0][2], rotationOriginal[index:]) #generates the best rotation
                    self.solutionARP.append(rotationOriginal) #save the feasible rotation (to be replaced) 
                    solution.saveAirportCap(rotationOriginal, airportDic) # update the airp. cap.(to be replaced)
                    noFlights += len(rotationOriginal[rotationOriginal['cancelFlight'] == 0])
                    noCancelledFlights +=  len(rotationOriginal[rotationOriginal['cancelFlight'] == 1])

                    delta1 = time.time() - start

                    solutionKpiExport.append([aircraft, delta1, len(flightRanges), noCombos, singletonList, len(solutionValue)])

                else:
                    rotation = self.fSNOTranspComSA[self.fSNOTranspComSA['aircraft'] == aircraft]
                    noFlights += len(rotation[rotation['cancelFlight'] == 0] )
                    noCancelledFlights += len(rotation[rotation['cancelFlight'] == 1])
                #import pdb; pdb.set_trace()
                aircraftSolList.append(aircraft) #add the aircraft w/ feasible solution
                print(aircraft, len(aircraftSolList), _noCombos)
            
            #import pdb; pdb.set_trace()
            _noCombos += 0.1 #increase the order of magnitude of the no. of combos
            aircraftTmpList = list(set(aircraftList) - set(aircraftSolList)) #check the differences between two lists
        
        dfSolutionKpiExport = pd.DataFrame(solutionKpiExport, columns = ["aircraft", "delta1", "noFlights", "noCombos", "singletonList", "noSolutions"])
        dfSolutionKpiExport.to_csv("dfSolutionKpiExport02.csv", header = True, index = False)

        return [-1]

    def findSolution(self):
        print("go delta1 aircraft _noCombos noAircrafts  noFlights noCancelledFlights ")
        solutionFound = [0]
        aircraftList =  list(self.aircraftDic.keys())
        go = 0
        while solutionFound[0] != -1:
            start = time.time()
            go += 1
            #print("let's go: ", go)
            random.seed(go)
            random.shuffle(aircraftList)
            self.solutionARP = []
            airportDic = copy.deepcopy(self.airportOriginaltDic)
            solutionFound = self.loopAircraftList(aircraftList, airportDic)
            #import pdb; pdb.set_trace()
            if solutionFound[0] == -1:
                print("Partial solution found!!!")
                self.fSNOTranspComSA = np.concatenate(self.solutionARP).ravel()
                #loop until recover

                for aircraft in aircraftList:
                    if('TranspCom' in aircraft):
                        continue
                    index, rotationOriginal = self.initialize(aircraft, airportDic, 0, False)
                    if(index != -1):
                        fixedFlights = self.domainFlights.fixed(rotationOriginal[index])
                        if fixedFlights['flight'] == rotationOriginal[index]['flight']:
                            continue
                        print(aircraft)
                        foundIndex = np.in1d(self.fSNOTranspComSA, rotationOriginal[index:]).nonzero()[0] #find the indices that need to be deleted
                        self.fSNOTranspComSA = np.delete(self.fSNOTranspComSA, foundIndex) #delete the indices
                        for  flight in rotationOriginal[index:]:
                            flight['cancelFlight'] = 1

                        self.fSNOTranspComSA = np.concatenate((self.fSNOTranspComSA, rotationOriginal[index:])) #add the new rotation to the solution

                        solution.airpCapRemove(rotationOriginal[index:], airportDic) #update airp. cap.
                        #import pdb; pdb.set_trace()
                        #self.repair(rotationOriginal[index:], airportDic)
                
                self.solutionARP = self.fSNOTranspComSA

            delta1 = time.time() - start
            print(go, delta1, solutionFound)
            #cost.total()
    
    def repair(self, rotation, airportDic):
        #cancel all the flights until the end of the rotation
        for  flight in rotation:
            flight['cancelFlight'] = 1
        solution.airpCapRemove(rotation, airportDic) #remove the remaining part of the rotation

if __name__ == "__main__":
    
    for path in paths.paths:
        start = time.time()
        arp = ARP(path)
        #cost.total(arp.flightScheduleSA, arp.itineraryDic, arp.configDic)
        arp.findSolution()
        solution.updateItin(arp.solutionARP, arp.itineraryDic)
        solution.export(arp.solutionARP, arp.itineraryDic, arp.minDate, path)
        delta1 = time.time() - start
        print("Solution time for the ARP: ", delta1)