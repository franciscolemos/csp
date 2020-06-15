import  numpy as np
def passengerDelay(flightScheduleSA, flightSchedule):
        fS = np.sort(flightSchedule['flightSchedule'], order = 'flightIndex') #ascend sort
        flight = flightSchedule['flightSchedule']['flight'][-1]
        import pdb; pdb.set_trace()
        
        fSSol = fS[fS['cancelFlight'] == 0]
        if len(fSSol) > 0:
            solDestination = fSSol['destination'][-1]
            if solDestination == originalDestination: 
                totalDelay = (fSSol['altArrInt'][-1] - fSSol['arrInt'][-1])
                if totalDelay > 0:
                    noPax = flightSchedule['count']
                    cabinRef = np.max(fS['cabin']) # max(node.cabinInt for node in i)
                    tripTypeRef = np.max(fS['trip']) # max(node.tripTypeInt for node in i)
                    coefCost = self.configDic['delay', cabinRef, tripTypeRef]
                    cost = noPax * totalDelay * coefCost
                    self.delay += cost #cont. increm. the total cost value
        return cost
def outTripCancel():
    pass
def inTripCancel():
    pass
def downgrade():
    pass
def cancelLegal():
    pass
def delayLegal():
    pass
def flightDecrease():
    pass
def flightIncrease():
    pass
def swap():
    pass
def nonCompliant():
    pass
def total(flightScheduleSA, itineraryDic, configDic):
    for itinerary, flightSchedule in itineraryDic.items():
        passengerDelay(flightScheduleSA, flightSchedule)
        outTripCancel()
        inTripCancel()
        downgrade()
        cancelLegal()
        delayLegal()
        flightDecrease()
        flightIncrease()
        swap()
        nonCompliant()