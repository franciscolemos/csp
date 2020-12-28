def cancelLoop(rotation, flightRanges): #cancel loop, starting on the first flight, to find feas. sol.
    origin = rotation[0]['origin'] #origin 
    combo = [0] * len(flightRanges)
    combo[0] = -1
    for index, flight in enumerate(rotation[1:], 1): #start at second flight
        if flightRanges[flight['flight']][0] == -1: #the first value is cancel
            if (flight['origin'] != origin):
                combo[index] = -1 #add cancel. to combo
            else:
                return tuple(combo)
        else: #singleton
            print("Singleton found")
            import pdb; pdb.set_trace()
            return False

def delayCancel(rotation, flightRanges):
    newCombo = [-2] * len(rotation) #new combo
    bestCombo = [-2] * len(rotation) #best combo
    bestSol = []
    tmpRotation = copy.deepcopy(rotation) #copy the original rotation
    
    for index, flight in enumerate(tmpRotation): #loop through the flights in the temp. rotation
        newCombo = copy.deepcopy(bestCombo)
        #import pdb; pdb.set_trace()
        for delay in flightRanges[flight['flight']]: #loop through the delays
            newFlight = copy.deepcopy(flight) #copy the curr. flight
            #if the solution is worse continue

            newCombo[index] = delay #delay is feasible [-1, -2, ... -2], [180, -1, ..., -2]
            _newCombo = [i for i in newCombo if i > -2] #full new combo [-180]
            newSol = solution.value(_newCombo) #full new sol. (0, 180, [180])
            
            #print("index:", index, "newCombo[index]:", newCombo[index], "_newCombo:", _newCombo, "newSol:", newSol, "bestSol:", bestSol)
            #import pdb; pdb.set_trace()

            if bestCombo[index] != -2: #the combo is init.
                if (bestSol[0] == 0) & (newSol[1] > bestSol[1]): #newSol has the same cancel and more delay
                    break
                if (newSol[0] < bestSol[0]): #newSol has more cancel. flights
                    continue
                if (newSol[0] == bestSol[0]) & (newSol[1] > bestSol[1]): #newSol has the same cancel and more delay
                    continue
              
            #print("index:", index, "newCombo:", newCombo[index], "_newCombo:", _newCombo, "newSol:", newSol)       
            if delay == -1: #cancel flight
                newFlight['cancelFlight'] = 1
                newFlight['altFlight'] = -1
            else:
                newFlight['cancelFlight'] = 0
                newFlight['altFlight'] = delay
                newFlight['altDepInt'] += delay
                newFlight['altArrInt'] += delay
            
            _tmpRotation = copy.deepcopy(tmpRotation)
            _tmpRotation[index] = newFlight #update the flight
            __tmpRotation = _tmpRotation[:index + 1]
            if len(feasibility.continuity(__tmpRotation[__tmpRotation['cancelFlight'] != 1])) > 0 :
                continue #infeasible
            if len(feasibility.TT(__tmpRotation[__tmpRotation['cancelFlight'] != 1])) > 0 :
                continue #infeasible
            
            tmpRotation = copy.deepcopy(_tmpRotation)
            bestCombo[index] = delay #[-1, -2, ... -2], [180, -1, ..., -2]
            bestSol = newSol
            

    #add verify sol. 
    return bestSol[2] #return the combo

def updateBestSol(self, bestSol, newSol):
    if len(bestSol) > 0:
        if newSol[0] > bestSol[0]:
            return newSol
        if newSol[1] < bestSol[1]:
            return newSol
        if newSol[1] == bestSol[1]: #same value for delay
            if max(newSol[2]) < max(bestSol[2]): #new sol. is less convoluted
                return newSol
    else:
        return newSol