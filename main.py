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

class ARP:
    def __init__(self, path):
        self.solution = {}
        self.visited = [] # Array to keep track of visited nodes.
        self.criticalFlight = []
        self.fixedFlights = []
        self.movingFlights = []
        self.flightRotationDic = readRotation.readRotation(path, "rotations.csv").read2FlightRotationDic() #{flightDate:aircraft}
        minDate = self.flightRotationDic['minDate']
        maxDate = self.flightRotationDic['maxDate']
        self.configDic = readConfig.readConfig(path, "config.csv", minDate).read2Dic()
        self.aircraftRotationDic = readRotation.readRotation(path, "rotations.csv").read2AircraftRotationDic() #{aircraft:flightSchedule}
        self.flightDic = readFlights.readFlights(path, "flights.csv").read2Dic()  
        self.aircraftDic = readAircrafts.readAircrafts(path, "aircraft.csv", minDate).read2Dic()
        self.altAircraftDic = readAltAircraft.readAltAircraft(path, "alt_aircraft.csv", minDate).read2Dic()
        self.altAirportSA = readAltAirports.readAltAirport(path, "alt_airports.csv", minDate).read2SA() #atttrib. of SA
        self.altFlightDic = readAltFlights.readAltFlights(path, "alt_flights.csv").read2Dic()
        self.distSA = readDist.readDist(path, "dist.csv").read2SA()
        i = schedules.initialize(self.aircraftRotationDic, self.altAircraftDic, self.altFlightDic, 
            self.aircraftDic, self.flightDic, path, minDate)
        i.aircraftSchedule() #included flight and aircr. disr. and, maint. {aircraft:flightSA}
        self.aircraftScheduleDic = i.aircraftScheduleDic #1 aircraft to n flights
        i.flightSchedule()
        self.flightScheduleSA = i.flightScheduleSA #all the flights + room to un-cancel flights for airport cap. purpose
        self.itineraryDic = [] # readItineraries.readItineraries(path,"itineraries.csv").read2Dic(self.flightScheduleSA, self.distSA)
        #determine the planning horizon
        endDateTime = datetime.combine(datetime.date(self.configDic['endDate']),
            datetime.time(self.configDic['endTime']))
        if maxDate < endDateTime:
            self.flightRotationDic['maxDate'] = endDateTime 
            maxDate = endDateTime 
        noDays = fD.dateDiffDays(maxDate, minDate) + 1 # + 1 day for arr. next()
        self.fSNOTranspComSA = self.flightScheduleSA[self.flightScheduleSA['family'] != "TranspCom"]
        self.airportDic = readAirports.readAirports(path, "airports.csv", noDays, self.altAirportSA, []).read2Dic() #does not include noDep/noArr 

        scenario.echo(len(self.flightDic), len(self.aircraftDic), len(self.airportDic),
                    len(self.itineraryDic), len(self.altFlightDic), len(self.altAircraftDic),
                    len(self.altAirportSA), noDays - 1)
        self.solutionARP = []

    def initialize(self, aircraft):
        #TODO
        #check if rotation includes maint.
        #if it includes maint. it has to be removed
        
        rotation = self.fSNOTranspComSA[self.fSNOTranspComSA['aircraft'] == aircraft]
        rotation = rotation[rotation['cancelFlight'] == 0] #only flying flights
        rotation = np.sort(rotation, order = 'altDepInt') #sort ascending
        #check rotation feasibility
        infContList = feasibility.continuity(rotation) #cont.
        infTTList = feasibility.TT(rotation) #TT
        
        rotationMaint = np.sort(self.aircraftScheduleDic[aircraft], order = 'altDepInt') #select the aircr. and sort the rotation
        rotationMaint = rotationMaint[rotationMaint['flight'] == 'm']
        infMaintList = []
        if len(rotationMaint) > 0:
            infMaintList = feasibility.maint(rotationMaint) #maint.
        
        infDepList = feasibility.dep(rotation, self.airportDic) #airp. dep. cap.
        infArrList = feasibility.arr(rotation, self.airportDic) #airp. arr. cap.

        feasible = len(infContList) + len(infTTList) + len(infMaintList) + len(infDepList) + len(infArrList)
        if feasible == 0:
            self.solutionARP.append(rotation) #save the feasible rotation
            solution.saveAirportCap(rotation, self.airportDic) #update the airp. cap.
            return -1
        else:
            index = min(np.concatenate((infContList, infTTList, infMaintList, infDepList, infArrList), axis = None)) #find tme min. index; wgere the problem begins
            import pdb; pdb.set_trace()
            return index

        #visualize the graphs
    def findSolution(self):

        aircraftList =  list(self.aircraftDic.keys())
        #might have to change this to most constr. flights: maint. airp./flights
        random.shuffle(aircraftList)
        for aircraft in aircraftList:
            #aircraft = "A318#33"
            print(aircraft, self.aircraftDic[aircraft])
            index = self.initialize(aircraft) #save a feasible rotation or return the index of inf.
            if index != -1: #found a feas. solution in initialize()
                index = 0
                dfs = aD.dfs(data, self.solution) #init. class in actions layer
                while(index != -1): #search the solution
                    startFlight = data.flightSchedule[index] #starting flight to start the dfs
                    index = dfs.dfs(self.visited, data.graphFs, startFlight)
                    if(index != -1): #solution not found
                        pass
                        #define the critical flight
                        #delete the loop files (backtrack)
                        #update the flightSchedule with partial solution
                        #save the partial solution
                        #create new solution from the flightSchedule
                    print(dfs.solution)
                    pdb.set_trace()
                
                self.solutionARP.append(rotation) #save the feasible rotation
                solution.saveAirportCap(rotation, self.airportDic) #update the airp. cap.

if __name__ == "__main__":
    for path in paths.paths:
        #add while loop
        ARP(path).findSolution()





"""
self.solution = {
    '724001/03/08':[],
    '724301/03/08':[],
    '286601/03/08':[],
    '286701/03/08':[],
    '530301/03/08':[],
    '530002/03/08':[],
    'm':[],
    '736602/03/08':[],
    '736902/03/08':[],
    '737002/03/08':[]
}
"""