import dal.classesRoadef as ROADEF
import numpy as np
from numpy import genfromtxt
from dal.classesDtype import dtype as dt
import pdb

class readDist:
    def __init__(self, path, file):
        self.path = path
        self.file = file
        self.f = open(self.path + "\\" +  self.file, encoding="utf8")
        self.distSA = []
        self.dtypeD = np.dtype([('origin', np.unicode, 3), ('destination', np.unicode, 3),
            ('dist', np.int16), ('tripType', np.unicode, 1)])

    def read2SA(self):
        tmpDistSA = genfromtxt(self.path + "\\" +  self.file, delimiter=' ', dtype = self.dtypeD)
        self.dtypeD = np.dtype(self.dtypeD.descr + [('trip', np.int8)]) #update dtype to include
        y = len(tmpDistSA) #length of the array
        self.distSA = np.zeros(y, self.dtypeD) #initialize the str. array
        #self.distSA[0:y] = tmpDistSA #copy the array
        self.distSA['origin'] = tmpDistSA['origin'] 
        self.distSA['destination'] = tmpDistSA['destination']
        self.distSA['dist'] = tmpDistSA['dist']
        self.distSA['tripType'] = tmpDistSA['tripType']
        for dist, distInt in dt.distInt.items(): #loop array
            self.distSA['trip'][self.distSA['tripType'] == dist]= distInt #hash dist
        return self.distSA


    