import numpy as np
from recovery.actions import solution
import copy
import time
from itertools import product
from recovery.actions import ARPUtils
from recovery.actions import feasibility

class upperHeuristic:
    def __init__(self, solutionARP, configDic, domainFlights, _rotationMaint, _noCombos):
        self.solutionARP = solutionARP
        self.configDic = configDic
        self.domainFlights = domainFlights
        self._rotationMaint = _rotationMaint
        self._noCombos = _noCombos

    def solve(self, flightRanges, rotation, index, aircraft):
        start = time.time()
        feasibility.verifyFlightRanges(flightRanges, rotation, index) #check if flight ranges has the same size of rotation[index:]
        rotationMaint = []
        if len(self._rotationMaint) > 0:
            rotationMaint = ARPUtils.addMaint(aircraft, self._rotationMaint) #creates the maint to be later added to the rotation
        lIndex = index
        flightRangesCopy = copy.deepcopy(flightRanges) #copy of the current flight ranges
        uIndex, partialFlightRanges, sizeRanges = self.upperIndex(lIndex, rotation, flightRangesCopy) #get the upper index and the respecive flight ranges
        flightCombinations = product(*partialFlightRanges.values()) #find all the combinations
        flightRangesRemaining = self.removeFlightRanges(flightRangesCopy, rotation[uIndex:]) #flightRanges - upper rotation
        self.verifyLengths(rotation, lIndex, partialFlightRanges, flightRangesRemaining)
        
        solutionValue = [] #initializes the solution value for later appraisal
        solutions = np.array(list(flightCombinations))
        fixedRotation = copy.deepcopy(rotation)
        while True:
            bestSol = []
            self.verifyComboRotation(solutions[0], fixedRotation[lIndex:uIndex])
            for combo in solutions:
                newSol = self.verifyBestSol(bestSol, combo)
                if not newSol: continue
                   
                rotationCopy = copy.deepcopy(fixedRotation) #will be used to test the solution because the delays and cancellations cannot be incremental
                luAllContraints = ARPUtils.luAllContraints(combo, rotationCopy, lIndex, uIndex) #matches the partialFlightRanges with rotationCopy
                if luAllContraints == -1:
                    continue
                if luAllContraints == -2: #airp. cap. problem
                    print("Cap. problem in combo@upperHeuristic.py")
                    import pdb; pdb.set_trace()
                    return 1, aircraft, self._noCombos #, len(aircraftSolList),  noFlights, noCancelledFlights 
                
                bestSol = newSol # self.updateBestSol(bestSol, newSol)
            solution.newPartialRotation(bestSol[2], fixedRotation[lIndex:uIndex])

            if(uIndex == len(fixedRotation)):
                return fixedRotation
            lIndex = uIndex
            uIndex, partialFlightRanges, sizeRanges = self.upperIndex(lIndex, fixedRotation, flightRangesCopy)
            flightCombinations = product(*partialFlightRanges.values()) #find all the combinations
            flightRangesRemaining = self.removeFlightRanges(flightRangesCopy, fixedRotation[uIndex:]) #flightRanges - upper rotation
            self.verifyLengths(rotation, lIndex, partialFlightRanges, flightRangesRemaining)
            solutions = np.array(list(flightCombinations))

            #print(uIndex, partialFlightRanges, sizeRanges )
            #print(bestSol)

    def upperIndex(self, lIndex, rotation, fr):
        size = 1
        uIndex = lIndex
        partialFlightRanges = {}
        for flight in rotation[lIndex:]: #loop through the rotation
            v = fr[flight['flight']]
            size *= len(v)
            if size > self._noCombos * 10**5:
                return uIndex, partialFlightRanges, sizeRanges
            uIndex += 1
            partialFlightRanges[flight['flight']] = v
            sizeRanges = size
        return uIndex, partialFlightRanges, sizeRanges

    def removeFlightRanges(self, flightRangesCopy, rotation):
        flightRangesRemaining = {}
        for flight in rotation:
            flightRangesRemaining[flight['flight']] = flightRangesCopy[flight['flight']]
        return flightRangesRemaining
    
    def verifyBestSol(self, bestSol, combo):
        newSol = solution.value(combo)
        if len(bestSol) > 0: #propagation
            if (newSol[0] < bestSol[0]): #newSol has more cancel. flights
                return False
            if (newSol[0] == bestSol[0]) & (newSol[1] > bestSol[1]): #newSol has the same cancel and more delay
                return False
        return newSol
    
    def verifyLengths(self, rotation, lIndex, partialFlightRanges, flightRangesRemaining):
        if len(rotation[:lIndex]) + len(partialFlightRanges) + len(flightRangesRemaining) != len(rotation):
            print("Diff. sizes in the flight ranges and the rotation")
            print(len(rotation[:lIndex]), len(partialFlightRanges), len(flightRangesRemaining), len(rotation))
            import pdb; pdb.set_trace()
    
    def verifyComboRotation(self, combo, rotation):
        if len(combo) != len(rotation):
            print("Diff. sizes in combo and the recovery rotation part")
            print(len(combo), len(rotatio))
            import pdb; pdb.set_trace()

    def removeSingleton(self, singletonList, airpCapCopy, aircraftSolList, rotation, index):
        while len(singletonList) >= 1: #[(flight, 'dep')]
            airc2Cancel = solution.singletonRecovery(self.solutionARP, singletonList, airpCapCopy, self.configDic) 
            if airc2Cancel == -1:
                import pdb; pdb.set_trace()
                return 1 #, aircraft, _noCombos, len(aircraftSolList),  noFlights, noCancelledFlights
            else:
                print("airc2Cancel: ", airc2Cancel)
                airportDic = copy.deepcopy(airpCapCopy) #update airportDic
                aircraftSolList = list(set(aircraftSolList) - set([airc2Cancel])) #remove the aircraft from aircraftSolList
                rotationPop = self.solutionARP.pop(airc2Cancel, None) #remove the rotation from self.solutionARP
                flightRanges, noCombos, singletonList, totalCombos = self.domainFlights.ranges(rotation[index:], airpCapCopy) #_noCombos = -1, delta = 1
