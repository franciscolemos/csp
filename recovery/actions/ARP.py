"""
Aircraft recovery problem (ARP) algorithm
==========================================

Abstract
_________

The ARP.py files is the main file to find solutions for the ARP. this is where all the logic is stored. Initially the module loads the data for aircraft, airport capacity, congigurations for the recovery time window, distances, flight schedules, aircraft rotation, itineraries, aircraft position and disruptions. After the data is loaded a set of data structures are created in order to determine for each aircraft if its rotation is feasible. If the aircraft's rotation is feasible it is added to the ARP solution and airport capacity is updated.

If the aircraft's rotation is infeasible, the model will use an algorithm to find the airport time slots with available departure and arrival capacity for each of the flights of the aircraft rotation. The result of the latter is a a set of vectors, whose cross product will determine the search space to find a solution. Each search space size is compared with the size with a limit value starting at 10,000 combinations. If the search space is wthin the limit the algorithm will find all the feasible solutions for the infeasible aircraft rotation and accept the one that has least flight cancellations followed by the least amount of delay.

The previous paragraphs describe constraint satisfaction programming (CSP). By first inserting the feasible aircraft rotations, we will reduce the airport capacity, which in turn will reduce the search space to find feasible domains for the infeasible aircraft rotation flights.

On the other hand, if the search space is graeter than the limit value the algorithm continues to the next aircraft rotation. After lopping through all the aircraft the limit value for the search spece size is increase by 10,000. When the limit value is graeter than 80,000 we use a genetic algorithm to find feasible solutions in a reasonable computing time. From the set of feasible solutions obtained the algorithm will accept the best, using the same criteria followed by CSP 
Finally, after finding feasible solutions for all the aircraft rotations the ARP algorithm terminates.

"""
from recovery.repositories import *
import collections
from datetime import datetime
import recovery.actions.funcsDate as fD
from recovery.actions import scenario
from recovery.actions import domains #domains is updated at each iteration
import time
import copy
import numpy as np
from recovery.actions import feasibility
from recovery.actions import solution
from itertools import product, chain
import pandas as pd
from recovery.dal.classesDtype import dtype as dt
from recovery.actions import cost
import random
from recovery.actions.funcsDate import int2DateTime
from recovery.actions import ARPUtils
from recovery.dal.classesDtype import gaType as gt
from recovery.actions.upperHeuristic import upperHeuristic
from recovery.actions.btf import flightPlan as fp
class ARP:
    """ """
    def __init__(self, path):
        """

        Args:
            path (str): Path to the data set
        
        Attributes:
            flightRotationDic(dict): flight aircraft
            minDate(datetime.datetime): Date of the first day starting at 00:00
            configDic(dict): configuration data for data instance
            aircraftRotationDic(dict): aircraft and respective flights
            flightDic(dict): flightnumber and the respective origin, destination departure and arrival times
            maxFlight(int): flight number maximum value 
            aircraftDic(dict):
            aircraftSA():
            altAircraftDic(dict):
            altAirportSA():
            altFlightDic(dict):
            distSA():
            aircraftScheduleDic():
            flightScheduleSA():
            fSNOTranspComSA():
            airportOriginaltDic():

        """
        self.dataSet = path.split("/")[-1]
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
        flightOrder =  collections.OrderedDict(sorted(self.flightDic.items())) #order dictionary
        self.maxFlight = flightOrder.popitem()[0] #get the value for the last key = max. flight
        self.aircraftDic, self.aircraftSA = readAircrafts.readAircrafts(path, "aircraft.csv", self.minDate).read2Dic()
        self.altAircraftDic = readAltAircraft.readAltAircraft(path, "alt_aircraft.csv", self.minDate).read2Dic()
        self.altAirportSA = readAltAirports.readAltAirport(path, "alt_airports.csv", self.minDate).read2SA() #atttrib. of SA
        self.altFlightDic = readAltFlights.readAltFlights(path, "alt_flights.csv").read2Dic()
        self.distSA = readDist.readDist(path, "dist.csv").read2SA()
        i = schedules.initialize(self.aircraftRotationDic, self.altAircraftDic, self.altFlightDic, 
            self.aircraftDic, self.flightDic, path, self.minDate)
        self.aircraftScheduleDic = i.aircraftSchedule() #included flight and aircr. disr. and, maint. {aircraft:flightSA} #1 aircraft to n flights
        self.flightScheduleSA = i.flightSchedule() #all the flights + room to un-cancel flights for airport cap. purpose
        self.itineraryDic = readItineraries.readItineraries(path,"itineraries.csv").read2Dic()
        #determine the planning horizon
        endDateTime = datetime.combine(datetime.date(self.configDic['endDate']),
            datetime.time(self.configDic['endTime']))
        if maxDate < endDateTime:
            self.flightRotationDic['maxDate'] = endDateTime 
            maxDate = endDateTime 
        noDays = fD.dateDiffDays(maxDate, self.minDate) + 1 # + 1 day for arr. next()
        self.fSNOTranspComSA = self.flightScheduleSA[self.flightScheduleSA['family'] != "TranspCom"]
        ##################### Start BTF ########################
        flightPlan = fp.flightPlan(self.distSA)
        flightPlan.fSDistModel(self.fSNOTranspComSA)
        flightPlan.fsPTF() #init. the total flight time and fuel consumed for each of flights
        import pdb; pdb.set_trace()
        ##################### End BTF ##########################
        self.airportOriginaltDic = readAirports.readAirports(path, "airports.csv", noDays, self.altAirportSA, []).read2Dic() #does not include noDep/noArr 
        #import pdb; pdb.set_trace()
        scenario.echo(len(self.flightDic), len(self.aircraftDic), len(self.airportOriginaltDic),
                    len(self.itineraryDic),
                    #-1,
                    len(self.altFlightDic), len(self.altAircraftDic),
                    len(self.altAirportSA), noDays - 1)

        self.domainFlights = domains.flights(self.configDic)
        
        self.solutionARP = {}

    def initialize(self, aircraft, airportDic, delta = 1, saveAirportCap = True): #check if the roation is feasible
        """
        This method retrieves the rotation for the specific aircraft. It afterwards checks if there are any flight slots  available to create new flights to counter the effect of disruption cause by flight cancellation or aircraft broken periods. In the case of flight creation, a new rotation is created to replaces the original one and the maximum flight number is updated.

        The algorithm then follows by filtering the aircraft rotation so that it only has flight that are not cancelled and saving it to a temporary aircraft rotation. This aircraft rotation is sorted by departure time (the latter already considers the delays induced by disruption) and its continuity and transit time feasibility is checked. Maintenance is added to the aircraft rotation in the form of satic flight and feasibility is checked. The last feasibility checks regard airport departure and arrival capacity. For each of the feasibility checks the index of every infeasibility is recorded.


        Args:
            aircraft (str): Aircraft whose rotation is to be evaluated for feasibility

        """
        rotationOriginal = self.fSNOTranspComSA[self.fSNOTranspComSA['aircraft'] == aircraft]
        #rotationOriginal = rotationOriginal[rotationOriginal['flight']!= ''] #remove created flights
        if len(rotationOriginal[rotationOriginal['flight'] == '']):
            aircDisr =  self.altAircraftDic.get(aircraft, None) #check if the airc. has broken period
            if aircDisr != None: #check if the airc. has broken period
                rotationOriginal, self.maxFlight = ARPUtils.newAircraftFlights(rotationOriginal, self.distSA, 
                self.maxFlight, aircDisr['endInt'], self.configDic) #create new flights and update self.maxFlight
                feasibility.verifyNullFlights(rotationOriginal)#verify if there are any null flights

                #consider using available airc.
                #generates feasible solution however it is not appropriate to handle other types of disruption
                #it is necessary to implement GA
            else: #the fligth has been cancelled
                rotationOriginal, self.maxFlight = ARPUtils.newFlights(rotationOriginal, self.distSA, 
                self.maxFlight, -1, self.configDic)
        
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
                    self.solutionARP[aircraft] = rotationOriginal #save the feasible rotation w/ cancelled flights
                    solution.saveAirportCap(rotation, airportDic) #update the airp. cap. only w/ cancelFlight == 0
                return -1, [] #for repair to determine if the problem is dep. or arr.
            else:
                #print("infeasiblities:", infContList, infTTList, infMaintList, infDepList, infArrList)
                
                index = min(np.concatenate((infContList, infTTList, infMaintList, infDepList, infArrList), axis = None)) #find tme min. index; wgere the problem begins
                #firstFlight = rotationOriginal[rotationOriginal['depInt'] >= self.configDic['startInt']][0]
                #index = np.in1d(rotationOriginal, firstFlight).nonzero()[0]
                return int(index), np.sort(rotationOriginal[rotationOriginal['cancelFlight'] == 0], order = 'altDepInt')  #because it has to include the aircraft to export the solution
        except Exception as e:
            print("Exception initialize:", e)
            import pdb; pdb.set_trace()
        #visualize the graphs
    
    def loopAircraftList(self, aircraftList, airportDic): 
        """
        This method loops through  the aircraft list. If the aircraft's rotation is feasible, it is added to the solution and the airport capacity is updated. If not then starting from the flight where the infeasibility lies, the algorithm tries to find the domains for each of the flights, the number of combinations and the list of singletons. The domains, consist of a set of vectors with time slots where there is available airport departure and arrival capacity. The number of  combinations consists consists of the number of rows resulting from the cross product of the vectors. A singleton consists of a flight that has domain of zero.

        Args:
            aircraftList (list<str>): Aircraft list
            airportDic(dict): Dictionary with the capacity for departures and arrivals for every airport 

        """
        import copy; aircraftTmpList = copy.deepcopy(aircraftList)
        solutionKpiExport = []
        noFlights = 0
        noCancelledFlights = 0
        aircraftSolList = [] #list of aircraft that have a feasibe rotation
        _noCombos = 0.1 #order of magnitude for the no. of combos
        infAirc = []
        feasible = -1
        START_COMBO = gt.START_COMBO
        STEP_COMBO = gt.STEP_COMBO
        while len(aircraftSolList) != len(aircraftList): #verify if the lists have the same size
            remainAirc = len(list(set(aircraftList) - set(aircraftSolList)))
            for aircraft in aircraftTmpList: #iterate through the aircraft list
                print(aircraft)
                if('TranspCom' in aircraft): #immediatly add the surface transport
                    aircraftSolList.append(aircraft)
                    rotation = self.flightScheduleSA[self.flightScheduleSA['aircraft'] == aircraft]
                    self.solutionARP[aircraft] = rotation
                    continue
                index, rotationOriginal  = self.initialize(aircraft, airportDic) #save a feasible rotation or return the index of inf.
                
                if(index != -1): #search the solution
                    rotation = copy.deepcopy(rotationOriginal) #copy the original rotation 
                    fixedFlights = self.domainFlights.fixed(rotation[index:]) #find the fixed flights: disrupted and outside RTW
                    if fixedFlights.size == 0: #if there are no fixed flights
                        movingFlights = rotation[index:]
                    else:#if there are fixed flights remove them from the remianing rotation
                        movingFlights = np.setdiff1d(rotation[index:], fixedFlights) 
                    airpCapCopy = copy.deepcopy(airportDic) #copy the airp. cap. solution
                     #flight ranges and combinations only for moving flight after disruption index with updated airp. cap. for fixed flights
                    flightRanges, noCombos, singletonList, totalCombos = self.domainFlights.ranges(rotation[index:], airpCapCopy, _noCombos)
                    
                    # if aircraft == 'A320#46':
                    #     import pdb; pdb.set_trace()

                    if (noCombos == -1): #excessive no. combos
                        if len(self._rotationMaint) > 0:
                            import pdb; pdb.set_trace()
                            continue
                        if totalCombos > START_COMBO:
                            uh = upperHeuristic(self.solutionARP, self.configDic, self.domainFlights, self._rotationMaint, _noCombos)
                            uh.removeSingleton(singletonList, airpCapCopy, aircraftSolList, rotation, index)
                            fixedRotation = uh.solve(flightRanges, rotation, index, aircraft)
                            
                            ####################### start of taxi flights ###############
                            solRot = fixedRotation[fixedRotation['cancelFlight'] == 0] #later will be used to pick first flight
                            if len(solRot) > 0: # the rotation can have all flights cancelled
                                solRot = np.sort(solRot, order = 'altDepInt')
                                originAirport = self.aircraftDic[aircraft]['originAirport']
                                initPosFeas = feasibility.initialPosition(solRot[0], originAirport)
                                if len(initPosFeas) > 0: #infeas. init. pos.
                                    fixedRotation, self.maxFlight = ARPUtils.wipRecover2(aircraft, self.altAircraftDic,self.distSA, originAirport, solRot, airportDic,
                                        fixedRotation, self.configDic, self.maxFlight)
                            ###################### end of taxi flights ##################
                            # if aircraft == 'A320#46':
                            #     import pdb; pdb.set_trace()                            
                            convertRotation = ARPUtils.convertFlight(fixedRotation[(fixedRotation['newFlight'] == 1) 
                                            & (fixedRotation['cancelFlight'] == 0)]
                                            , self.minDate) #if a new flight is delayed for the next day converts it
                            fixedRotation[(fixedRotation['newFlight'] == 1) 
                                            & (fixedRotation['cancelFlight'] == 0)] = convertRotation
                            # print(fixedRotation)
                            # import pdb; pdb.set_trace() 
                            self.solutionARP[aircraft] = fixedRotation #save the feasible rotation (to be replaced) 
                            solution.saveAirportCap(fixedRotation, airportDic) # update the airp. cap.(to be replaced)
                        else:
                            continue
                    else:
                        while len(singletonList) >= 1: #[(flight, 'dep')]
                            #import pdb; pdb.set_trace()
                            airc2Cancel = solution.singletonRecovery(self.solutionARP, singletonList, airpCapCopy, self.configDic) 
                            if airc2Cancel == -1:
                                import pdb; pdb.set_trace()
                                return 1, aircraft, _noCombos, len(aircraftSolList),  noFlights, noCancelledFlights
                            else:
                                print("airc2Cancel: ", airc2Cancel)
                                airportDic = copy.deepcopy(airpCapCopy) #update airportDic
                                aircraftSolList = list(set(aircraftSolList) - set([airc2Cancel])) #remove the aircraft from aircraftSolList
                                rotationPop = self.solutionARP.pop(airc2Cancel, None) #remove the rotation from self.solutionARP
                                flightRanges, noCombos, singletonList, totalCombos = self.domainFlights.ranges(rotation[index:], airpCapCopy) #_noCombos = -1, delta = 1
                        ############## end loop until all singletons removed ###########

                        start = time.time()
                        feasibility.verifyFlightRanges(flightRanges, rotation, index) #check if flight ranges has the same size of rotation[index:]
                        rotationMaint = []
                        if len(self._rotationMaint) > 0:
                            rotationMaint = ARPUtils.addMaint(aircraft, self._rotationMaint) #creates the maint to be later added to the rotation
                        flightCombinations = product(*flightRanges.values()) #find all the combinations
                        solutionValue = [] #initializes the solution value for later appraisal
                        solutions = np.array(list(flightCombinations))
                        bestSol = []
                        for combo in solutions: #loop through the possible combinations
                            newSol = solution.value(combo)
                            if len(bestSol) > 0: #propagation
                                if (newSol[0] < bestSol[0]): #newSol has more cancel. flights
                                    continue
                                if (newSol[0] == bestSol[0]) & (newSol[1] > bestSol[1]): #newSol has the same cancel and more delay
                                    continue
                            
                            allConstraints = ARPUtils.allConstraints(rotationOriginal, combo, index 
                            , movingFlights, fixedFlights, airpCapCopy, self._rotationMaint, rotationMaint) #check the sol. feas.
                            if allConstraints == -1:
                                continue
                            if allConstraints == -2: #airp. cap. problem
                                return 1, aircraft, _noCombos, len(aircraftSolList),  noFlights, noCancelledFlights 
                            
                            if len(bestSol) > 0:
                                if newSol[0] > bestSol[0]:
                                    bestSol = newSol
                                    continue
                                if newSol[1] < bestSol[1]:
                                    bestSol = newSol
                                    continue
                                if newSol[1] == bestSol[1]: #same value for delay
                                    if max(newSol[2]) < max(bestSol[2]): #new sol. is less convoluted
                                        bestSol = newSol 
                            else:
                                bestSol = newSol
                        try:
                            solution.newRotation(bestSol[2], rotationOriginal[index:]) #generates the best rotation
                        except:
                            delta1 = time.time() - start
                            print(aircraft, delta1, len(flightRanges), noCombos, singletonList, len(solutionValue))
                            import pdb; pdb.set_trace()
                        ####################### start of taxi flights ###############
                        solRot = rotationOriginal[rotationOriginal['cancelFlight'] == 0] #later will be used to pick first flight
                        if len(solRot) > 0: # the rotation can have all flights cancelled
                            solRot = np.sort(solRot, order = 'altDepInt')
                            originAirport = self.aircraftDic[aircraft]['originAirport']
                            initPosFeas = feasibility.initialPosition(solRot[0], originAirport)
                            if len(initPosFeas) > 0: #infeas. init. pos.
                                rotationOriginal, self.maxFlight = ARPUtils.wipRecover2(aircraft, self.altAircraftDic, self.distSA, originAirport, solRot, airportDic,
                                    rotationOriginal, self.configDic, self.maxFlight)
                        ###################### end of taxi flights ##################

                        self.solutionARP[aircraft] = rotationOriginal #save the feasible rotation (to be replaced) 
                        solution.saveAirportCap(rotationOriginal, airportDic) # update the airp. cap.(to be replaced)
                        noFlights += len(rotationOriginal[rotationOriginal['cancelFlight'] == 0])
                        noCancelledFlights +=  len(rotationOriginal[rotationOriginal['cancelFlight'] == 1])

                        delta1 = time.time() - start
                        solutionKpiExport.append([aircraft, delta1, len(flightRanges), noCombos, singletonList, len(solutionValue), bestSol[2]]) #df.iloc[0][2]]

                else:
                    rotation = self.fSNOTranspComSA[self.fSNOTranspComSA['aircraft'] == aircraft] #update
                    noFlights += len(rotation[rotation['cancelFlight'] == 0] ) #update
                    noCancelledFlights += len(rotation[rotation['cancelFlight'] == 1]) #update
                #import pdb; pdb.set_trace()
                aircraftSolList.append(aircraft) #add the aircraft w/ feasible solution
                print(aircraft, len(aircraftSolList), _noCombos)
            
            #import pdb; pdb.set_trace()
            START_COMBO -= STEP_COMBO #decrease the start combo for GA
            _noCombos += 0.1 #increase the order of magnitude of the no. of combos
            aircraftTmpList = list(set(aircraftList) - set(aircraftSolList)) #check the differences between two lists
            aircraftTmpList.sort()

        dfSolutionKpiExport = pd.DataFrame(solutionKpiExport, columns = ["aircraft", "delta1", "noFlights", "noCombos", "singletonList", "noSolutions", "solution"])
        dfSolutionKpiExport.to_csv("KPI03/dfSolutionKpiExport03_"+self.dataSet+".csv", header = True, index = False)

        return [feasible, infAirc]

    def findSolution(self):
        print("go delta1 aircraft _noCombos noAircrafts  noFlights noCancelledFlights ")
        solutionFound = [0]
        aircraftList = self.aircraftSA['aircraft'] 
        #aircraftList = list(self.aircraftDic.keys())
        #import pdb; pdb.set_trace()
        go = 0
        while solutionFound[0] != -1:
            start = time.time()
            go += 1
            #aircraftList.sort()
            #random.seed(go)
            #random.shuffle(aircraftList)
            self.solutionARP = {}
            airportDic = copy.deepcopy(self.airportOriginaltDic)
            solutionFound = self.loopAircraftList(aircraftList, airportDic) #airportDic will be updated
            #import pdb; pdb.set_trace()
            if solutionFound[0] == -1:
                print("Partial feasible solution found!!!")
                solutionARP = []
                for rotation in self.solutionARP.values(): #convert the sol. into no array
                    solutionARP.append(rotation)
                self.fSNOTranspComSA = np.concatenate(solutionARP).ravel()

                #verify the partial solution
                for aircraft in aircraftList: #verify if the solution is feasible
                    if('TranspCom' in aircraft):
                        continue
                    index, rotationOriginal = self.initialize(aircraft, airportDic, 0, False)
                    if(index != -1):
                        print('infeasible partial solution')
                        #import pdb; pdb.set_trace()
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
            else:
                print("Inf. sol.")
                import pdb; pdb.set_trace()
            delta1 = time.time() - start
            print(go, delta1, solutionFound)
            #cost.total()
    
    def repair(self, rotation, airportDic):
        #cancel all the flights until the end of the rotation
        for  flight in rotation:
            flight['cancelFlight'] = 1
        solution.airpCapRemove(rotation, airportDic) #remove the remaining part of the rotation
