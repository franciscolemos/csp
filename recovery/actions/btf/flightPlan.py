"""
flightPlan.py
====================================
This module loads the airport features (e.g. geographical coordinates, taxi-out time), 
default values for flight phases, aircraft engines dataset
 """
import sys
import recovery.actions.btf.headDist
import geomag
import numpy as np
from numpy import genfromtxt
from numpy import array
import recovery.repositories.btf.classesMeasures as CM
import recovery.actions.btf.plot as pl
from recovery.dal.btf.classesDtype import dtype as dt
import recovery.actions.btf.flightPhases as fP
import recovery.actions.btf.headDist as hD
import recovery.repositories.btf.readAirportsDat as  rAD
import pandas as pd
import statistics
from scipy import stats
import os
import copy

class flightPlan:
    """ """
    def __init__(self, distSA):
        """
        The constructor initializes airport coordinates, taxi times, landing and take-off data and aircraft engines performance

        Args:
            distSA (dtypeD): numpy array with flight time and type between each airport pair

        """
        self.distSA = distSA
        self.fSDistSA = []
        self.dtypeFSD = dt.dtypeFSD
        self.fsDistDic = {}
        self.modelDic = {}
        self.aircROCDSA = {}
        self.fsRocdDic = {}
        self.airportsDat = rAD.airport() #airport data
        self.airportsDatSA = self.airportsDat.airportsDatSA
        self.airportTaxiTimeSA = self.airportsDat.airportTaxiTimeSA #taxi times for airports
        self.aircraftDefaultSA = self.airportsDat.aircraftDefaultSA #
        self.aircraftEngineSA = self.airportsDat.aircraftEngineSA #aircraft engines
        self.engineLTOSA = self.airportsDat.engineLTOSA
        self.cumulPhaseSA = []
        self.flightDic = {}
        self.btfDic = {}
        self.flightDF = pd.DataFrame(columns=['key', 'origin', 'model', 'destination', 'cumulTime', 'physDist', 'cumulConsumedFuel'])
        self.flightScrapeDic = {}
        self.flightNotArrivedSA = []
        self.flightArrivedSA = []
    def fSDistModel(self, fSNOTranspComSA): #flight schedule dist. and model PTF
        """
        This method reads airport coordinates, calculates the bearing of the trajectory, the physical distance between two airports. The function derives the cruise altitude based on the physical distance.

        Args:
            fSNOTranspComSA (dtypeFS): Flight schedule
            
        """
        unknownAirp = []
        a = 0
        _hD = hD.headDist()
        for f in fSNOTranspComSA:
            if self.airportsDatSA['latitudeAirport'][self.airportsDatSA['iataAirport'] == f['origin']].size == 0:
                continue
            latOriginAirport = self.airportsDatSA['latitudeAirport'][self.airportsDatSA['iataAirport'] == f['origin']][0]
            lonOriginAirport = self.airportsDatSA['longitudeAirport'][self.airportsDatSA['iataAirport'] == f['origin']][0]
            if self.airportsDatSA['latitudeAirport'][self.airportsDatSA['iataAirport'] == f['destination']].size == 0:
                continue
            latDestinationAirport = self.airportsDatSA['latitudeAirport'][self.airportsDatSA['iataAirport'] == f['destination']][0]
            lonDestinationAirport = self.airportsDatSA['longitudeAirport'][self.airportsDatSA['iataAirport'] == f['destination']][0]
            
            bearing = _hD.heading((latOriginAirport, lonOriginAirport), (latDestinationAirport, lonDestinationAirport))
            geomagHeading = geomag.mag_heading(bearing,dlat=latOriginAirport,dlon=lonOriginAirport)
            physDist = _hD.haversine((latOriginAirport, lonOriginAirport), (latDestinationAirport, lonDestinationAirport))
            
            bearingPhysDistFlSA = dt.bearDistFl[(dt.bearDistFl['lBound'] <= geomagHeading) & (dt.bearDistFl['uBound'] > geomagHeading)]
            physDistFlSA = bearingPhysDistFlSA['response']
            flSA = physDistFlSA[(physDistFlSA['lDist'] <= physDist) & (physDistFlSA['uDist'] > physDist)]
            if flSA.size == 0:
                continue
            model = f['aircraft'].split("#")[0] #airc. model
            if not model in self.modelDic: #prevent the file from being read
                self.modelDic[model] = genfromtxt("./recovery/btf/dataSets/aircraftData/" + dt.PTF2CsvDic[model], delimiter=',', skip_header = 1, dtype = dt.aircROCD)

            maxFl = self.modelDic[model]['fl'][-1] #max. fl   
            fl = flSA['fl'][0] #airc. operating fl
            if maxFl < fl:
                a += 1
                continue
            windSpeed = flSA['windSpeed'][0]
            intensity = flSA['intensity'][0]
            year = 2000  + int(f['flight'][-2:]) #to determine taxiOut and taxiIn time
            self.fsDistDic[f['flight']] = {'origin':f['origin'] , 'destination':f['destination'], 'year':year,
                'model':model, 'physDist':physDist, 'fl':fl, 'windSpeed':windSpeed, 'intensity':intensity }

    def fsPTF(self):
        """
            This method loops through the flight schedule and derives the flight phases for taxi-out, take-off, climb, cruise, descent, approach and landing, and taxi-in
        """
        # blockFuel = []
        # blockTime =[]
        _fP = fP.flightPhases(self.airportsDat) #flight phases 
        i = 0
        for fs in self.fsDistDic.items(): #loop through the flight schedule
            origin = fs[1]['origin']
            model = fs[1]['model']
            destination = fs[1]['destination']
            key = origin+model+destination
            if key in self.flightDic: #verify is dict. entry exists
                continue
            else:
                rocdSA = self.modelDic[model] #struct. array with the aircraft's PTF
                size = len(rocdSA[rocdSA['fl'] == fs[1]['fl']]) #check if the flight level exists
                if size > 0:
                    size = len(rocdSA[rocdSA['fl'] <= fs[1]['fl']])
                else:
                    size = len(rocdSA[rocdSA['fl'] < fs[1]['fl']]) + 1
                #taxi-out, take-off, climb-out
                originICAO = self.airportsDatSA['icaoAirport'][self.airportsDatSA['iataAirport'] == fs[1]['origin']][0]
                year = fs[1]['year']
                aircraftEngine = self.aircraftEngineSA[self.aircraftEngineSA['modelBADA'] == model]#det. the set of available engines
                if len(aircraftEngine) == 0: #if there isn't any available aircraft model
                    print("There is no available available aircraft model for ", model)

                if len(aircraftEngine) == 1: #if there is only a sinlge aircraft moldel
                    engine = aircraftEngine['engineId'] #engine type
                    noEngines = aircraftEngine['noEngine'] #no. engines
                else: #choose the most common engine
                    for aE in aircraftEngine:
                        if aE['aircraft'][-2:] == b'**':
                            engine = aE['engineId']
                            noEngines = aE['noEngine']
                            break
                        else:
                            continue
                #departure
                departureSA = _fP.departure(engine, noEngines, originICAO, year) #
                #climb
                climbSA = _fP.interpolClimb(rocdSA, size, fs) #determine climbSA
                #descent
                descentSA = _fP.interpolDesc(rocdSA, size, fs)
                #approach + landing, taxi-in
                destinationICAO = self.airportsDatSA['icaoAirport'][self.airportsDatSA['iataAirport'] == fs[1]['destination']][0]
                arrivalSA = _fP.arrival(engine, noEngines, destinationICAO, year)
                #cruise
                cruiseDist = fs[1]['physDist']*1000 - (climbSA['cumulGndDist'][-1] + descentSA['cumulGndDist'][-1]) #[m]
                cruiseSA = _fP.interpolCruise(rocdSA, fs, cruiseDist)
                #normalizing flight phases
                normalDepartureSA = copy.deepcopy(departureSA)
                normalClimbSA = _fP.normalClimb(climbSA, departureSA)
                normalCruiseSA = _fP.normalCruise(cruiseSA, normalClimbSA)
                normalDescentSA = _fP.normalDescent(descentSA, normalCruiseSA)
                normalArrivalSA = _fP.normalArrival(arrivalSA, normalDescentSA, fs[1]['physDist']*1000) #last param. cumulGndDist [m]
                cumulPhaseSA = np.concatenate((normalDepartureSA, normalClimbSA, normalCruiseSA, normalDescentSA, normalArrivalSA))
                #import pdb; pdb.set_trace()
                #print(fs[1])
                # blockFuel.append([int(departureSA['cumulConsumedFuel'][-1]),
                #     int(climbSA['cumulConsumedFuel'][-1]), int(cruiseSA['cumulConsumedFuel'][-1]),
                #     int(descentSA['cumulConsumedFuel'][-1]),
                #     int(arrivalSA['cumulConsumedFuel'][-1]),
                #     int(cumulPhaseSA['cumulTime'][-1]/36)/100,
                #     int(cumulPhaseSA['cumulGndDist'][-1]/1000)])

                # blockTime.append([int(departureSA['cumulTime'][-1]/36)/100,
                #      int(climbSA['cumulTime'][-1]/36)/100,
                #      int(cruiseSA['cumulTime'][-1]/36)/100,
                #      int(descentSA['cumulTime'][-1]/36)/100,
                #      int(arrivalSA['cumulTime'][-1]/36)/100])

                self.flightDic[key] = -1
                #print(origin, model, destination)
                try:
                    self.flightDF.loc[i] = [key, origin, model, destination, 
                        int(int(cumulPhaseSA['cumulTime'][-1])/60), 
                        int(fs[1]['physDist']), 
                        int(cumulPhaseSA['cumulConsumedFuel'][-1])]
                    # self.btfDic[key] = {'cumulTime':int(int(cumulPhaseSA['cumulTime'][-1])/60), 
                    #     'physDist':int(fs[1]['physDist'])}
                    i += 1
                except:
                    continue
            #import pprint; pprint.pprint(cumulPhaseSA);
            #plot.dicSet(fs, cumulPhaseSA) #plot model's ff, altitude, ground dist.
            #pl.dicCdgA320Bcn(fs, cumulPhaseSA) #plot model's altitude, ground dist. for flight CDG to BCN w/ A320
            #plot.oriAircDestDic(fs, cumulPhaseSA) #plot model's altitude, ground dist. for flight CDG to BCN w/ A320
        # from pprint import pprint
        # pprint(blockFuel)
        # pprint(blockTime)
        # pdb.set_trace()
        self.flightDF.to_csv('./recovery/btf/results/flightPlanList.csv',index=False)
    
    def fsBTF(self, fs, configDic): #loop through flightDF and update flight sched.
        startInt = configDic['startInt']
        endInt = configDic['endInt']
        fsFilter = fs[(fs['depInt'] == fs['altDepInt']) & (fs['depInt'] >= startInt) & (fs['depInt'] <= endInt)]
        for flight in fsFilter:
            newTime = self.flightDF[(self.flightDF['origin'] == flight['origin']) &
                (self.flightDF['model'] == flight['family']) &
                (self.flightDF['destination'] == flight['destination'])]['cumulTime']
            if len(newTime) > 0:
                indices = np.in1d(fs, flight).nonzero()[0]
                for i in indices:
                    fs[i]['arrInt'] = fs[i]['depInt'] + newTime
                    fs[i]['altArrInt'] = fs[i]['altDepInt'] + newTime

                # flight['arrInt'] = flight['depInt'] + newTime
                # flight['altArrInt'] = flight['altDepInt'] + newTime
        return fs    
        # import pdb; pdb.set_trace()



        # for index, flight in self.flightDF.iterrows():
        #     newfs  = fs[(fs['origin'] == flight['origin']) & (fs['destination'] == flight['destination']) & (fs['family'] == flight['model'])]
        #     if len(newfs) == 0:
        #         #print("unexisting flight schedule:", flight['origin'], flight['destination'], flight['model'])
        #         continue
        #     indices = np.in1d(fs, newfs).nonzero()[0]
        #     for i in indices:
        #         fs[i]['arrInt'] = fs[i]['depInt'] + flight['cumulTime']
        #         fs[i]['altArrInt'] = fs[i]['altDepInt'] + flight['cumulTime']
        # return fs

    def descStat(self):
        flightArrivedSA = genfromtxt('./dataSets/flightAware/flightListArrived.csv', 
            delimiter=',', dtype = dt.flightHistory) #read the flightListArrived.csv
        flightList = []
        for index, row in self.flightDF.iterrows():#read the flight flight DF
            key = row['key']
            model =  row['model']
            time = row['cumulTime']
            flightSA = flightArrivedSA[(flightArrivedSA['idFlight'] == key) & (flightArrivedSA['aircraft'] == model)]
            sampleSize = len(flightSA)
            if sampleSize == 0:
                continue
            row['modelPercentile'] = stats.percentileofscore(flightSA['durationInt'], time)
            row['modelRMSE'] = self.rmse(flightSA['durationInt'], time)
            row['roadefTime'] = self.distSA['dist'][(self.distSA['origin'] == row['origin']) & (self.distSA['destination'] == row['destination'])][0]
            row['roadefPercentile'] = stats.percentileofscore(flightSA['durationInt'], row['roadefTime'])
            row['roadefRMSE']   = self.rmse(flightSA['durationInt'], row['roadefTime'])
            row['sampleSize'] = sampleSize
            row['sampleMean'] = statistics.mean(flightSA['durationInt'])
            row['sampleMedian'] = statistics.median(flightSA['durationInt'])
            flightList.append(row)
            
        #BTF model and ROADEF RMSE vs. others

        if len(sys.argv) > 1:
            argv1 = sys.argv[1]
        else:
            argv1 = 't'
        if  argv1 == 't':
            labelRMSE ='ROADEF RMSE'  #RMSE label
            labelPerc = 'ROADEF percentile' #Perc. lablel
        elif argv1 == 'f':
            labelRMSE = 'Lido RMSE'  #RMSE label
            labelPerc = 'Lido percentila' #Perc. lablel    



        flightStatsDF = pd.DataFrame(flightList)
        physDist = flightStatsDF['physDist']
        modelRMSE = flightStatsDF['modelRMSE']
        roadefRMSE = flightStatsDF['roadefRMSE']
        decorFuelFlow = [{'x':physDist, 'y':[modelRMSE, roadefRMSE],
                'legend': 'RMSE vs. distance',
                'legendLoc':0,
                'xLabel':'Distance [Km]',
                'xRange':np.arange(min(physDist)/2, max(physDist)+100, 100 ),
                'yLabel':'RMSE [min]' ,
                'ySeries':['BTF model RMSE', labelRMSE ],
                'yRange':np.arange(0, max(modelRMSE) + 15, 10),
                'graphTitle':'RMSE vs. distance'}] #,
        pl.graphScatter(decorFuelFlow)

        #Model and ROADEF percentile vs. distance
        modelPercentile = flightStatsDF['modelPercentile']
        roadefPercentile = flightStatsDF['roadefPercentile']
        decorFuelFlow = [{'x':physDist, 'y':[modelPercentile, roadefPercentile],
                'legend': 'Percentile vs. distance',
                'legendLoc':0,
                'xLabel':'Distance [Km]',
                'xRange':np.arange(min(physDist)/2, max(physDist)+100, 100 ),
                'yLabel':'Percentile' ,
                'ySeries':['BTF model percentile', labelPerc ],
                'yRange':np.arange(0, max(modelPercentile) + 15, 10),
                'graphTitle':'Percentile vs. distance'}] #,
        pl.graphScatter(decorFuelFlow)
        import pdb; pdb.set_trace()
        flightStatsDF.to_csv('.results/flightStats_lido.csv')
        pdb.set_trace()
    def rmse(self, flightTimeSA, time):
        y_test = flightTimeSA
        #sampleSize = len(flightTimeSA)
        y_pred = time
        #combined rmse value
        rss = ((y_test-y_pred)**2).sum()
        mse = np.mean((y_test-y_pred)**2)
        rmse = np.sqrt(mse)
        return rmse