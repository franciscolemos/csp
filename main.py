# Using a Python dictionary to act as an adjacency list
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
    solution.updateItin(arp.solutionARP, arp.itineraryDic)
    solution.export(arp.solutionARP, arp.itineraryDic, arp.minDate, path)
    delta1 = time.time() - start
    print("Solution time for the ARP: ", delta1)