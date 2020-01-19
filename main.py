# Using a Python dictionary to act as an adjacency list
import pdb
import numpy as np
from repositories import *
import actions.dfs2 as aD #it is not necessary to import the entire package, only some modules
from actions import domains #domains is updated at each iteration
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
        self.aircraftDic = readAircrafts.readAircrafts(path, "alt_aircraft.csv", minDate).read2Dic()
        self.altAircraftDic = readAltAircraft.readAltAircraft(path, "alt_aircraft.csv", minDate).read2Dic()
        self.altAirportSA = readAltAirports.readAltAirport(path, "alt_airports.csv", minDate).read2SA() #atttrib. of SA
        self.altFlightDic = readAltFlights.readAltFlights(path, "alt_flights.csv").altFlight.read2Dic()


        self.dist = readDist.readDist(path, "dist.csv").read2SA()
        import pdb; pdb.set_trace()
        self.airportCapDic = copy.deepcopy(airportCap.airportCapDic) #keep de original solution

    def initialize(self):
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
        domainsFlights = domains.flights(data.configDic, flightSchedule.fs)
        self.fixedFlights = domainsFlights.fixed()
        self.movingFlights = np.setdiff1d(flightSchedule.fs, self.fixedFlights,True)
        domainsFlights.remove(self.airportCapDic, self.movingFlights) #removes flights from airp.
        domainsFlights.criticalMaint()
        #TODO
        #initialize ranges 
        domainsFlights.ranges(self.movingFlights) #it is necessary because of forward checking
        #test the ranges
        

    def findSolution(self):
        self.initialize()
        index = 0
        dfs = aD.dfs(data, self.solution) #init. class in actions layer
        while(index != -1):
            startFlight = data.flightSchedule[index] #starting flight to start the dfs
            index = dfs.dfs(self.visited, data.graphFs, startFlight)
            if(index != -1): #solution not found
                pass
                #define the critical flight
                #delete the loop files
                #update the flightSchedule with partial solution
                #save the partial solution
                #create new solution from the flightSchedule
            print(dfs.solution)
            pdb.set_trace()

if __name__ == "__main__":
    for path in paths.paths:
        ARP(path).findSolution()