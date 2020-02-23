# Using a Python dictionary to act as an adjacency list
import pdb
import numpy as np
from repositories import *
import actions.funcsDate as fD
from datetime import datetime
from actions import domains #domains is updated at each iteration
import actions.dfs2 as aD #it is not necessary to import the entire package, only some modules
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
        self.dist = readDist.readDist(path, "dist.csv").read2SA()

        i = schedules.initialize(self.aircraftRotationDic, self.altAircraftDic, self.altFlightDic, 
            self.aircraftDic, self.flightDic, path, minDate)
        i.aircraftSchedule() #included flight and aircr. disr. and, maint. {aircraft:flightSA}
        self.aircraftScheduleDic = i.aircraftScheduleDic #1 aircraft to n flights
        i.flightSchedule()
        self.flightScheduleSA = i.flightScheduleSA #all the flights + room to un-cancel flights for airport cap. purpose
        #determine the planning horizon
        endDateTime = datetime.combine(datetime.date(self.configDic['endDate']),
            datetime.time(self.configDic['endTime']))
        if maxDate < endDateTime:
            self.flightRotationDic['maxDate'] = endDateTime 
            maxDate = endDateTime 
        noDays = fD.dateDiffDays(maxDate, minDate) + 1 # + 1 day for arr. next()
        self.fSNOTranspComSA = self.flightScheduleSA[self.flightScheduleSA['family'] != "TranspCom"]
        self.airportDic = readAirports.readAirports(path, "airports.csv", noDays, self.altAirportSA, []).read2Dic() #does not include noDep/noArr 

    def initialize(self, aircraft):
        #TODO
        rotation = self.fSNOTranspComSA[self.fSNOTranspComSA['aircraft'] == aircraft]
        
        import pdb; pdb.set_trace()
        #check rotation feasibility
        #cont.
        #TT
        #maint.
        #airp. dep. cap.
        #airp. arr. cap.

        #if feasible 
        #save the solution
        #update the airp. cap.
        # return -1

        #else
        #initialize the domains
        domainsFlights = domains.flights(data.configDic, flightSchedule.fs)
        self.fixedFlights = domainsFlights.fixed()
        self.movingFlights = np.setdiff1d(flightSchedule.fs, self.fixedFlights,True)
        domainsFlights.remove(self.airportCapDic, self.movingFlights) #removes flights from airp.
        domainsFlights.criticalMaint()
        #TODO
        #initialize ranges 
        domainsFlights.ranges(self.movingFlights) #it is necessary because of forward checking
        #test the ranges
        #initialize the solution/solutions/graphs to be traversed
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
        #visualize the graphs
    def findSolution(self):

        aircraftList =  list(self.aircraftDic.keys())
        random.shuffle(aircraftList)
        for aircraft in aircraftList:
            print(aircraft, self.aircraftDic[aircraft])
            index = self.initialize(aircraft) #initialize all the variables of the flight sched.
            if index != -1: #found a feas. solution in initialize()
                index = 0
                dfs = aD.dfs(data, self.solution) #init. class in actions layer
                while(index != -1):
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

if __name__ == "__main__":
    for path in paths.paths:
        #add while loop
        ARP(path).findSolution()