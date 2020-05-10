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
import random
import copy
import time
from itertools import product

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
        self.airportDic = readAirports.readAirports(path, "airports.csv", noDays, self.altAirportSA, []).read2Dic() #does not include noDep/noArr 

        scenario.echo(len(self.flightDic), len(self.aircraftDic), len(self.airportDic),
                    len(self.itineraryDic),
                    #-1,
                    len(self.altFlightDic), len(self.altAircraftDic),
                    len(self.altAirportSA), noDays - 1)

        self.domainFlights = domains.flights(self.configDic)

        self.solutionARP = []

    def initialize(self, aircraft): #check if the roation is feasible
        rotation = self.fSNOTranspComSA[self.fSNOTranspComSA['aircraft'] == aircraft]

        rotation = rotation[(rotation['cancelFlight'] == 0) & (rotation['flight']!= '')] #only flying flights
        rotation = np.sort(rotation, order = 'altDepInt') #sort ascending
        #check rotation feasibility
        infContList = feasibility.continuity(rotation) #cont.
        infTTList = feasibility.TT(rotation) #TT
        
        rotationMaint = np.sort(self.aircraftScheduleDic[aircraft], order = 'altDepInt') #select the aircr. and sort the rotation
        _rotationMaint = rotationMaint[rotationMaint['flight'] == 'm'] #find if the rotation has maint. scheduled
        infMaintList = []
        if len(_rotationMaint) > 0:
            infMaintList = feasibility.maint(rotationMaint) # find if maint. const. is infeas.
        
        infDepList = feasibility.dep(rotation, self.airportDic) #airp. dep. cap.
        infArrList = feasibility.arr(rotation, self.airportDic) #airp. arr. cap.
        try:
            feasible = len(infContList) + len(infTTList) + len(infMaintList) + len(infDepList) + len(infArrList)

            #print("feasible:", len(infContList), len(infTTList), len(infMaintList), len(infDepList), len(infArrList))
            if feasible == 0:
                self.solutionARP.append(rotation) #save the feasible rotation
                solution.saveAirportCap(rotation, self.airportDic) #update the airp. cap.
                return -1, []
            else:
                
                    #print("infeasiblities:", infContList, infTTList, infMaintList, infDepList, infArrList)
                    index = min(np.concatenate((infContList, infTTList, infMaintList, infDepList, infArrList), axis = None)) #find tme min. index; wgere the problem begins
                    return int(index), rotation #because it has to include the aircraft to export the solution
        except Exception as e:
            print("Exception initialize:", e)
            import pdb; pdb.set_trace()
        #visualize the graphs
    
    def findSolution(self):

        aircraftList =  list(self.aircraftDic.keys())
        #random.shuffle(aircraftList)
        import copy; aircraftTmpList = copy.deepcopy(aircraftList)
        print("aircraft _noCombos stage noCombos remainAirc len(aircraftSolList)")
        aircraftSolList = [] #list of aircraft that have a feasibe rotation
        start = time.time()
        _noCombos = 0.1

        while len(aircraftSolList) != len(aircraftList): #verify if the lists have the same size
            remainAirc = len(list(set(aircraftList) - set(aircraftSolList)))
            for aircraft in aircraftTmpList: #iterate through the aircraft list
                if('TranspCom' in aircraft): #immediatly add the surface transport
                    aircraftSolList.append(aircraft)
                    rotation = self.flightScheduleSA[self.flightScheduleSA['aircraft'] == aircraft]
                    self.solutionARP.append(rotation)
                    continue

                index, rotationOriginal = self.initialize(aircraft) #save a feasible rotation or return the index of inf.
                
                print(aircraft, _noCombos, "feasible", -3, remainAirc, len(aircraftSolList))
                solutionFound = 0
                if(index != -1): #search the solution
                    rotation = copy.deepcopy(rotationOriginal) #copy the original rotation 
                    fixedFlights = self.domainFlights.fixed(rotation[index:]) #find the fixed flights: disrupted and outside RTW
                    if fixedFlights.size == 0: #if there are no fixed flights
                        movingFlights = rotation[index:]
                    else:#if there are fixed flights remove them from the remianing rotation
                        movingFlights = np.setdiff1d(rotation[index:], fixedFlights) 

                    #update airp. cap for moving flights
                    airpCapCopy = copy.deepcopy(self.airportDic) #copy the airp. cap. solution

                     #flight ranges and combinations only for moving flight after disruption index with updated airp. cap. for fixed flights
                    flightRanges, noCombos = self.domainFlights.ranges(rotation[index:], airpCapCopy, _noCombos)
                    
                    if noCombos == -1:
                        print(aircraft, _noCombos, "Excessive", noCombos, remainAirc, len(aircraftSolList))
                        continue #resume next aircraft
                    
                    if len(flightRanges) != len(rotation[index:]):
                        print("No. ranges diff. remaining flights")
                        import pdb; pdb.set_trace()

                    flightCombinations = product(*flightRanges.values()) #find all the combinations

                    for combo in flightCombinations: #generate the possible combinations
                        rotation = copy.deepcopy(rotationOriginal) #keep a copy of the original because of new rotation

                        #movingFlights = copy.deepcopy(copyMovingFlights)
                        if(len(combo) != len(rotation[index:])):
                            print("Combo size is diff. from remaining rotation")
                            import pdb; pdb.set_trace()

                        solution.newRotation(combo, rotation[index:])

                        if len(rotation) != len(rotation[:index]) + len(movingFlights) + len(fixedFlights):
                            print("Diff. in length")
                            import pdb; pdb.set_trace()

                        if -1 * len(combo) == sum(combo): #all flights are cancelled
                            continue 
                        
                        rotation = rotation[rotation['cancelFlight'] != 1] #only cancelled flights

                        if (len(feasibility.dep(rotation[index:], airpCapCopy)) > 0) | (len(feasibility.arr(rotation[index:], airpCapCopy)) > 0):
                            print("Airp. cap. exceed!")
                            #import pdb; pdb.set_trace()                        

                        if len(rotation[(rotation['previous'] != '0') & (rotation['previous'] != '')]) > 0: # because previous flight exist
                            if len(feasibility.previous(rotation)) > 0:
                                continue
                        if len(feasibility.previous(rotation)) > 0:
                            continue
                        if len(feasibility.continuity(rotation)) > 0:
                            continue #cont.
                        if len(feasibility.TT(rotation)) > 0:
                            continue
                        infMaintList = []
                        if len(feasibility.dep(rotation, airpCapCopy)) > 0: #use airpCapCopy because it has the fixed flights
                            continue #airp. dep. cap. (might not be necessary)
                        if len(feasibility.arr(rotation, airpCapCopy)) > 0: #use airpCapCopy because it has the fixed flights
                            continue #airp. arr. cap. (might not be necessary)
                        
                        value = solution.value(rotation)
                        
                        self.solutionARP.append(rotation) #save the feasible rotation (to be replaced) 
                        solution.saveAirportCap(rotation, self.airportDic) # update the airp. cap.(to be replaced)
                        #print(aircraft, _noCombos, "savedShitSolution", noCombos, remainAirc, len(aircraftSolList))
                        print("savedShitSolution", combo)
                        solutionFound = 1
                        break

                    if solutionFound == 0: #=> all flights must be cancelled
                        print("A solution was not found!")
                        counter = 0
                        for ranges in flightRanges.values():
                            rotation[index + counter]['cancelFlight'] = 1  if ranges[0] == -1 else ranges[0]
                            counter += 1
                        
                        self.solutionARP.append(rotation) #save the feasible rotation (to be replaced) 
                        solution.saveAirportCap(rotation, self.airportDic) # update the airp. cap.(to be replaced)
                        print(aircraft, _noCombos, "endCancel", noCombos, remainAirc, len(aircraftSolList))

                aircraftSolList.append(aircraft) #add the aircraft w/ feasible solution
                print(aircraft, _noCombos, "afterShitSolution", -2, remainAirc, len(aircraftSolList))
            _noCombos += 0.1
            aircraftTmpList = list(set(aircraftList) - set(aircraftSolList)) #check the differences between two lists
            print(aircraft, _noCombos, "newAircraftIteration", -2, remainAirc, len(aircraftSolList))
        delta1 = time.time() - start
        print(len(flightRanges), noCombos, delta1)
        # import pdb; pdb.set_trace()  

if __name__ == "__main__":
    for path in paths.paths:
        arp = ARP(path)
        arp.findSolution()
        solution.export(arp.solutionARP, arp.itineraryDic, arp.minDate, path)