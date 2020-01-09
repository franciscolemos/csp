import numpy as np
class flights:
    def __init__(self, configDic):
        self.configDic = configDic
        
    def fixed(self, fs): #flights that cannot be moved => empty domains
        fsOutRTW = fs[(fs['altDepInt'] < self.configDic['startInt']) | #flights outside RTW
                (fs['altDepInt'] > self.configDic['endInt'])] #flights outside RTW
        fsFixed = fs[(fs['delay'] > 0) & #flight disrupted
                    (fs['broken'] != 1) & #flight not broken
                    (fs['cancelFlight'] != 1) & #flight not cancelled
                    ((fs['altDepInt'] >= self.configDic['startInt']) & #flight inside RTW
                    (fs['altDepInt'] <= self.configDic['endInt']))] #flight inside RTW
        
        aircFlightOrderDic = np.concatenate([fsOutRTW, fsFixed])
        return aircFlightOrderDic #return first set of flights that