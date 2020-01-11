# Using a Python dictionary to act as an adjacency list
import pdb
import numpy as np
import repositories.data as data
import repositories.airportCap as aC
from repositories.flightSchedule import fs
import actions.dfs2 as aD
from actions import critical
from actions import domains

class ARP:
    def __init__(self):
        self.solution = {}
        self.visited = [] # Array to keep track of visited nodes.
        self.criticalFlight = []
        self.fixedFlights = []
        self.movingFlights = []
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
        self.criticalFlight = critical.flightMaint(fs) #define the critical flight
        domainsFlights = domains.flights(data.configDic)
        self.fixedFlights = domainsFlights.fixed(fs)
        self.movingFlights = np.setdiff1d(fs, self.fixedFlights,True)
        #TODO
        #(remove flights that can be moved)
        #initialize ranges 

    def findSolution(self):
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
    ARP()
    ARP().initialize() #initialize variables
    ARP().findSolution()