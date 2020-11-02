def initialize(self, aircraft, airportDic, delta = 1, saveAirportCap = True): #check if the roation is feasible
    pass

def addMaint(self, aircraft):
    """
    Add aircraft maintenance to the flight schedule
    
    Args:
        aircraftList (list<str>): Aircraft list
    """ 
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

def removeSingleton():
    pass