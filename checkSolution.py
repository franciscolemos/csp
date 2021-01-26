from  recovery.repositories.paths import pathList
import subprocess
import os
from datetime import datetime
import pandas as pd
from recovery.dal import resultsDtype
import numpy as np


sizeLine = {}
sizeLine['version'] = []
sizeLine['dateTime'] = []
sizeLine['dataInstance'] = []
sizeLine['checkAircraftBreakdownPeriod'] = []
sizeLine['checkAircraftCapacity'] = []
sizeLine['checkAircraftCreation'] = []
sizeLine['checkAircraftSwap'] = []
sizeLine['checkAirportCapacity'] = []
sizeLine['checkCancellationofCreatedRotation'] = []
sizeLine['checkFixedFlights'] = []
sizeLine['checkFlight'] = []
sizeLine['checkItinerary'] = []
sizeLine['checkPassengerReac'] = []
sizeLine['checkRotation'] = []
sizeLine['costs'] = []
today = datetime.now().strftime("%Y%m%d_%H%M")

for path in pathList:
    dataSet = path.split("/")[-1]
    print(dataSet)
    os.chdir(path)
    os.system("solutionChecker-win32.exe")
    sizeLine['version'] = '32/32 Remove depInt <> RTW'
    sizeLine['dateTime'].append(today)
    sizeLine['dataInstance'].append(dataSet)
    sizeLine['checkAircraftBreakdownPeriod'].append(os.path.getsize("./results/checkAircraftBreakdownPeriod.txt"))
    sizeLine['checkAircraftCapacity'].append(os.path.getsize("./results/checkAircraftCapacity.txt"))
    sizeLine['checkAircraftCreation'].append(os.path.getsize("./results/checkAircraftCreation.txt"))
    sizeLine['checkAircraftSwap'].append(os.path.getsize("./results/checkAircraftSwap.txt"))
    sizeLine['checkAirportCapacity'].append(os.path.getsize("./results/checkAirportCapacity.txt"))
    sizeLine['checkCancellationofCreatedRotation'].append(os.path.getsize("./results/checkCancellationofCreatedRotation.txt"))
    sizeLine['checkFixedFlights'].append(os.path.getsize("./results/checkFixedFlights.txt"))
    sizeLine['checkFlight'].append(os.path.getsize("./results/checkFlight.txt"))
    sizeLine['checkItinerary'].append(os.path.getsize("./results/checkItinerary.txt"))
    sizeLine['checkPassengerReac'].append(os.path.getsize("./results/checkPassengerReac.txt"))
    sizeLine['checkRotation'].append(os.path.getsize("./results/checkRotation.txt"))
    os.system("costChecker-win32.exe > results/cost.txt")
    costs = np.genfromtxt('results/cost.txt', delimiter=':')
    sizeLine['costs'].append(costs[-1][1])
    os.chdir("../../../")

dataSetSizes = pd.DataFrame(sizeLine)
try:
    dataSetSizes.to_csv('./results/prpInf.csv', mode='a', index=False, header = False)
except:
    import pdb; pdb.set_trace()
    dataSetSizes.to_csv('./results/prpInf.csv', mode='a', index=False, header = False)
