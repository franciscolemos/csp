"""
Algorithm
====================================

Abstract
_________

In this project we present a novel approach to recover disruption in commercial aviation. We use the ROADEF 2009 Challenge flight rotation and the current model finds soltions for the disrupted rotations. The model is decomposed into the aircraft recovery problem (ARP) and the passenger recovery problem (PRP). In the ARP we combine constraint satisfaction programming and a genetic algorithm to find an initial feasible solutions. In the PRP we use the shortest path to reallocate passengers to aircraft with available seating capacity to fly them for the place they are stranded to their destination.

"""

import sys
from recovery.actions import solution
import pdb
from recovery.actions import ARP

import time
from recovery.repositories import *

if __name__ == "__main__":
    start = time.time()
    try:
         path = sys.argv[1]
    except:
        path = paths.paths[0]
    dataSet = path.split("/")[-1]
    print("Dataset: ", dataSet)
    arp = ARP.ARP(path)
    # #cost.total(arp.flightScheduleSA, arp.itineraryDic, arp.configDic)
    arp.findSolution()
    solution.export2CSV(arp.solutionARP, dataSet)
    #arp.solutionARP = solution.importCSV(dataSet)
    solution.updateItin(arp.solutionARP, arp.itineraryDic, arp.newFlight)
    solution.export(arp.solutionARP, arp.itineraryDic, arp.minDate, path)
    delta1 = time.time() - start
    print("Solution time for the ARP: ", delta1)