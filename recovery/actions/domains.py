import numpy as np
import copy
from recovery.repositories.data import maxDelay
from recovery.repositories.data import deltaT
class flights:
    def __init__(self, configDic, fs):
        self.configDic = configDic
        self.fs = fs
        self.fsFixed = []
        self.airportCap = []
        self.criticalFligh = []
        self.domains = {}

    def fixed(self): #flights that cannot be moved => empty domains
        fsOutRTW = self.fs[(self.fs['altDepInt'] < self.configDic['startInt']) | #flights outside RTW
                (self.fs['altDepInt'] > self.configDic['endInt'])] #flights outside RTW
        fsFixed = self.fs[(self.fs['delay'] > 0) & #flight disrupted
                    (self.fs['broken'] != 1) & #flight not broken
                    (self.fs['cancelFlight'] != 1) & #flight not cancelled
                    ((self.fs['altDepInt'] >= self.configDic['startInt']) & #flight inside RTW
                    (self.fs['altDepInt'] <= self.configDic['endInt']))] #flight inside RTW
        fsMaint = self.fs[self.fs['idFlight'] == 'm'] #maint. is assumed to be a fixed flight
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
    
    def ranges(self, movingFlights): #only complying with airp. cap.
        for f in self.fs:
            domain = []
            if f in movingFlights: #
                for t in range(0, maxDelay, deltaT): #find the feasible time slots
                    origin = f['origin']
                    dep = f['altDepInt'] + t

                    destination = f['destination']
                    arr = f['altArrInt'] + t
                    if all([self.airportCap[origin][int(dep/60)]['noDep'] + 1 <= self.airportCap[origin][int(dep/60)]['capDep'],
                    self.airportCap[destination][int(arr/60)]['noArr'] + 1 <= self.airportCap[destination][int(dep/60)]['capDep']]):
                        #TODO
                        #limit the delay inside the RTW
                        domain.append(t/60)

                #if f in self.domains:
                    #continue
                #find the range
            self.domains[f['flight']] = domain
        return self.domains