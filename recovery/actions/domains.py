import numpy as np
import copy
from recovery.repositories.data import maxDelay
from recovery.repositories.data import deltaT
class flights:
    def __init__(self, configDic):
        self.configDic = configDic
        self.fsFixed = []
        self.criticalFligh = []

    def fixed(self, fs): #flights that cannot be moved => empty domains
        #import pdb; pdb.set_trace()
        fsOutRTW = fs[(fs['altDepInt'] < self.configDic['startInt']) | #flights outside RTW
                (fs['altDepInt'] > self.configDic['endInt'])] #flights outside RTW
        fsFixed = fs[(fs['depInt'] != fs['altDepInt']) & #flight is delayed
                    #(fs['broken'] != 1) & #flight not broken
                    (fs['cancelFlight'] != 1) & #flight not cancelled
                    ((fs['altDepInt'] >= self.configDic['startInt']) & #flight inside RTW
                    (fs['altDepInt'] <= self.configDic['endInt']))] #flight inside RTW
        fsMaint = fs[fs['flight'] == 'm'] #maint. is assumed to be a fixed flight
        self.fsFixed = np.concatenate([fsOutRTW, fsFixed, fsMaint])
        return self.fsFixed #return first set of flights that

    def remove(self, airportCap, movingFlights):
        for f in movingFlights:
            origin = f['origin']
            dep = f['altDepInt']
            airportCap[origin][int(dep/60)]['noDep'] -= 1
            destination = f['destination']
            arr = f['altArrInt']
            airportCap[destination][int(arr/60)]['noArr'] -= 1
        self.airportCap = copy.deepcopy(airportCap)
        return self.airportCap

    def criticalMaint(self):
        maintFlight = self.fs[self.fs['flight'] == 'm'] 
        airp = maintFlight['origin'][0]
        startInt = maintFlight['depInt'][0]
        self.criticalFligh = self.fs[(self.fs['destination'] == airp) & (self.fs['altArrInt'] <= startInt)][-1]
        #TODO
        #Initialize the domain
        return self.criticalFligh
    
    def ranges(self, movingFlights, airportDic): #only complying with airp. cap.
        domains = {}
        try:
            for f in movingFlights:
                domain = [-1] #add flight cancellation
                for t in range(0, maxDelay, deltaT): #find the feasible time slots
                    origin = f['origin']
                    dep = f['altDepInt'] + t
                    destination = f['destination']
                    arr = f['altArrInt'] + t
                    if all([airportDic[origin][int(dep/60)]['noDep'] + 1 <= airportDic[origin][int(dep/60)]['capDep'],
                        airportDic[destination][int(arr/60)]['noArr'] + 1 <= airportDic[destination][int(dep/60)]['capArr']]):
                        domain.append(t)
                domains[f['flight']] = domain
        except:
            print("Exception finding ranges@domains.py")
            import pdb; pdb.set_trace()
        return domains