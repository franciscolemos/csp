"""
flightPhases.py
=================
This module renders the departure, climb, descent and arrival phases
"""

import sys
import os
from recovery.dal.btf.classesDtype import dtype as dt
import recovery.repositories.btf.classesMeasures as CM
import recovery.actions.btf.flightPlan
import numpy as np
import math
import copy
import pdb

class flightPhases:
    """ """
    def __init__(self, airportsDat):
        """
        Args:
            airportsDat (dtypeAirp): Airport data
        """
        self.airportTaxiTimeSA = airportsDat.airportTaxiTimeSA
        self.aircraftDefaultSA = airportsDat.aircraftDefaultSA
        self.aircraftEngineSA = airportsDat.aircraftEngineSA
        self.engineLTOSA = airportsDat.engineLTOSA
        #pdb.set_trace()
        if len(sys.argv) > 1:
            argv1 = sys.argv[1]
        else:
            argv1 = 't'
        if  argv1 == 't':
            self.rocd = 'climbNom'
            self.ff = 'cruiseNom'
        elif argv1 == 'f':
            self.rocd = 'climbHi'
            self.ff = 'cruiseHi'
    def departure(self, engine, noEngines, originICAO, year, climb =  -1):
        """
        Args:
            engine (str): Aircraft engine model
            noEngines (int): Aircraft's number of engines 
            originICAO (str): Origin airport ICAO
            year(int): Year when the data was collected
        
        :returns:
            departureSA(rocdPTF): Departure phase comprising taxi-out, take-off and initial climb

        """
        size = 6 if climb == 30 else 4
        departureSA = np.zeros(size, dtype = dt.rocdPTF)
        #Taxi-out
        taxiOutTime = self.airportTaxiTimeSA['taxiOut' + str(year)][self.airportTaxiTimeSA['icaoAirport'] == originICAO][0]
        cumulTime = taxiOutTime 
        taxiOutFuel = self.engineLTOSA['fuelTaxi'][self.engineLTOSA['engineId'] == engine][0] #fuel rate [kg/sec./engine]
        fuelFlow = noEngines * taxiOutFuel
        consumedTaxiOutFuel = taxiOutTime * fuelFlow
        cumulConsumedFuel = consumedTaxiOutFuel 
        departureSA[0]['fuelFlowSec'] = fuelFlow #updated fuel flow
        departureSA[1] = (0, 0, cumulTime, 0, 0, 0, 0, 0, 0, fuelFlow,
                consumedTaxiOutFuel, cumulConsumedFuel)
        #Take off
        departureSA[2] = (0, 0, cumulTime, 0, 0, 0, 0, 0, 0, fuelFlow,
                consumedTaxiOutFuel, cumulConsumedFuel) #Start take-off
        takeOffTime = self.aircraftDefaultSA['timeSec'][self.aircraftDefaultSA['phase'] == 'takeOff'][0] #take off default time
        cumulTime += takeOffTime 
        takeOffFuel = self.engineLTOSA['fuelTakeOff'][self.engineLTOSA['engineId'] == engine][0] #fuel rate [kg/sec./engine]  
        fuelFlow = noEngines * takeOffFuel
        consumedTakeOffFuel = takeOffTime * fuelFlow
        cumulConsumedFuel += consumedTakeOffFuel
        departureSA[2]['fuelFlowSec'] = fuelFlow #updated fuel flow 
        departureSA[3] = (0, 0, cumulTime, 0, 0, 0, 0, 0, 0, fuelFlow,
                consumedTakeOffFuel, cumulConsumedFuel)
        #Climb out
        if climb == 30:
            departureSA[4] = (0, 0, cumulTime, 0, 0, 0, 0, 0, 0, fuelFlow,
                    consumedTakeOffFuel, cumulConsumedFuel) #start of climb-out
            climbOutTime = self.aircraftDefaultSA['timeSec'][self.aircraftDefaultSA['phase'] == 'climbOut'][0] #climb out default time
            cumulTime += climbOutTime 
            climbOutfuel = self.engineLTOSA['fuelClimb'][self.engineLTOSA['engineId'] == engine][0] #fuel rate [kg/sec./engine]
            fuelFlow =   noEngines * climbOutfuel
            consumedClimbOutFuel = climbOutTime * fuelFlow
            cumulConsumedFuel += consumedClimbOutFuel
            departureSA[4]['fuelFlowSec'] = fuelFlow #updated fuel flow
            departureSA[5] = (30, 0, cumulTime, 0, 0, 0, 0, 0, 0, fuelFlow,
                        consumedClimbOutFuel, cumulConsumedFuel) #30 is the climb out FL
        return departureSA
    def interpolClimb(self, rocdSA, size, fs):
        """
        Args:
            rocdSA (str): Numpy array with the aircraft's ROCD retrieved from the PTF
            size (int): Size of the aircraft's ROCD array
            
        
        :returns:
            climbSA(rocdPTF): Climb phase

        """
        m = CM.measures()
        i = 0 
        climbSA = np.zeros(size, dt.rocdPTF) #intialize the climb struct. array
        fl = 0
        time = 0
        cumulTime = 0
        climbHi = rocdSA[self.rocd][0]/60 #velocity to climb [ft/sec]
        dist = 0
        cumulDist = 0 #dist. measured in the air
        gama = 0
        gndDist = 0
        cumulGndDist = 0
        flMeter = 0
        fuelFlowSec = rocdSA['climbFFNom'][0]/60 #fuel flow for the cur./start fl [kg/sec]
        consumedFuel = 0
        cumulConsumedFuel = 0 

        climbSA[i] = (fl, climbHi, cumulTime, cumulDist, dist, 
                gama, gndDist, cumulGndDist, flMeter, fuelFlowSec,
                consumedFuel, cumulConsumedFuel) 

        for cur, nxt in zip(rocdSA[:size-1], rocdSA[1:size]): #interpol. through the PFT data struct.
            i += 1
            try:
                if fs[1]['fl'] >= nxt['fl']: #hasn't reach cruise altitude
                    deltaVertDist = (nxt['fl'] - cur['fl']) * 100 #space [ft]
                    fl = nxt['fl']
                    rocdClimb = nxt[self.rocd]/60 #rocdClimb [ft/sec]
                    tasClimb = nxt['climbTAS'] * m.knt2fts #tasClimb [ft/sec]
                    ffClimb = nxt['climbFFNom']/60 #ffClimb [kg/sec]
                else:
                    deltaVertDist = (fs[1]['fl'] - cur['fl']) * 100 #space [ft]
                    fl = fs[1]['fl']
                    rocdClimb = np.interp(fl, [cur['fl'], nxt['fl']], [cur[self.rocd], nxt[self.rocd]])/60 #rocdClimb [ft/sec]
                    tasClimb = np.interp(fl, [cur['fl'], nxt['fl']], [cur['climbTAS'], nxt['climbTAS']]) * m.knt2fts #tasClimb [ft/sec]
                    ffClimb = np.interp(fl, [cur['fl'], nxt['fl']], [cur['climbFFNom'], nxt['climbFFNom']])/60 #ffClimb [kg/sec]
                climbHi = cur[self.rocd]/60 #velocity to climb [ft/sec]
                if climbHi == 0:
                    print("xxxxxxxxxxx Div. by zero xxxxxxxxxxxxxxxxxxx")
                    #pdb.set_trace()
                accClimb = 0.5 * ((rocdClimb)**2 - (cur[self.rocd]/60)**2)/(fl*100 - cur['fl']*100) #1/2(v^2-v0^2)/(x-x0) [ft/sec.^2]
                time = ((rocdClimb - cur[self.rocd]/60)/accClimb) #(v-v0)/a time to cilmb [sec]
                cumulTime += time
                accTAS =  (tasClimb - cur['climbTAS']*m.knt2fts)/time
                dist = cur['climbTAS']*m.knt2fts* time + 0.5*accTAS*(time**2) 
                cumulDist += dist #[ft]
                gama = math.asin(deltaVertDist/dist) #opposed catet (fl height) divided by hypoth. [rad]
                gndDist = dist  * math.cos(gama) * m.ft2Meter #project the hypoth. on the ground [m]
                cumulGndDist += gndDist #[m]
                flMeter =  fl * 100 * m.ft2Meter #[m]
                accFF = (ffClimb - cur['climbFFNom']/60)/time #fuel flow rate of change
                consumedFuel = (cur['climbFFNom']/60)*time + 0.5*accFF*(time**2) #same principle as the movement eq.
                cumulConsumedFuel += consumedFuel #kg
                climbSA[i] = (fl, rocdClimb, cumulTime, cumulDist, dist, 
                    gama, gndDist, cumulGndDist, flMeter, ffClimb,
                    consumedFuel, cumulConsumedFuel)
            except Exception as e:
                print("Interpol. climb Exception: ", e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print( fname, exc_tb.tb_lineno)
                print(fl)

        return climbSA 
    def interpolDesc(self, rocdSA, size, fs):
        """
        Args:
            rocdSA (str): Numpy array with the aircraft's ROCD retrieved from the PTF
            size (int): Size of the aircraft's ROCD array
            
        
        :returns:
            descSA(rocdPTF): Descent phase

        """
        m = CM.measures()
        descSA = np.zeros(size, dt.rocdPTF) #intialize the descend. struct. array
        cumulTime = 0 
        cumulDist = 0 #dist. measured in the air
        cumulGndDist = 0 #dist. measured in the ground 
        cumulConsumedFuel = 0 #
        revRocdSA = rocdSA[::-1] #revert the rocd array
        fl = fs[1]['fl'] 
        i = 0
        time = 0
        cumulTime = 0
        
        if fl in rocdSA['fl']: #find if the FL is in the SA
            descentNom = rocdSA['descentNom'][rocdSA['fl'] == fl]/60 #velocity to desc. [ft/sec]
            fuelFlowSec = rocdSA['descentFF'][rocdSA['fl'] == fl]/60 #fuel flow for the cur./start fl [kg/sec]
        else:
            for cur, nxt in zip(revRocdSA[:-1], revRocdSA[1:]): #interpol. through the PFT data struct.
                if nxt['fl'] >= fl:
                    continue
                fuelFlowSec = np.interp(fl, [nxt['fl'], cur['fl']], [nxt['descentFF'], cur['descentFF']])/60 #fuel flow for the cur./start fl [kg/sec]
                descentNom = np.interp(fl, [nxt['fl'], cur['fl']], [nxt['descentNom'], cur['descentNom']])/60 #velocity to descent [ft/sec]
                break
            # import pdb; pdb.set_trace()
            # print("FL not %5d in table" % fl )

        dist = 0
        cumulDist = 0 #dist. measured in the air
        gama = 0
        gndDist = 0
        cumulGndDist = 0
        flMeter = 0
        consumedFuel = 0
        cumulConsumedFuel = 0 
        descSA[i] = (fl, descentNom, cumulTime, cumulDist, dist, 
                gama, gndDist, cumulGndDist, flMeter, fuelFlowSec,
                consumedFuel, cumulConsumedFuel)
        for cur, nxt in zip(revRocdSA[:-1], revRocdSA[1:]): #interpol. through the PFT data struct.
            if nxt['fl'] >= fl:
                continue
            else:
                try:
                    if cur['fl'] > fl and nxt['fl'] < fl: #to calculate the, descentTAS, rocd, fuel flow
                        descentTAS = np.interp(fl, [nxt['fl'], cur['fl']], [nxt['descentTAS'], cur['descentTAS']])* m.knt2fts # using the descent TAS get the hypoth. [ft]
                        fuelFlowSec = np.interp(fl, [nxt['fl'], cur['fl']], [nxt['descentFF'], cur['descentFF']])/60 #fuel flow for the cur./start fl [kg/sec]
                        descentNom = np.interp(fl, [nxt['fl'], cur['fl']], [nxt['descentNom'], cur['descentNom']])/60 #velocity to descent [ft/sec]
                    else:
                        descentTAS = cur['descentTAS'] * m.knt2fts # using the descent TAS get the hypoth. [ft]
                        fuelFlowSec = cur['descentFF']/60 #fuel flow for the cur./start fl [kg/sec]
                        descentNom = cur['descentNom']/60 #velocity to descenf [ft/sec]
                        fl = cur['fl']
                    i += 1
                    accDescent = 0.5 * ((nxt['descentNom']/60)**2 - (descentNom)**2)/(nxt['fl']*100 - fl*100 ) #1/2(v^2-v0^2)/(x-x0) [ft/sec.^2]
                    time = ((nxt['descentNom']/60 - descentNom)/accDescent) #(v-v0)/a time to cilmb [sec]
                    cumulTime += time
                    accTAS =  (nxt['descentTAS']* m.knt2fts - descentTAS)/time
                    dist = descentTAS* time + 0.5*accTAS*(time**2) 
                    cumulDist += dist #[ft]
                    #airDist = time/3600 * cur['climbTAS'] #[NM]
                    gama = math.asin((nxt['fl'] - fl)/dist) #opposed catet (fl height) divided by hypoth. [rad]
                    gndDist = dist  * math.cos(gama) * m.ft2Meter #project the hypoth. on the ground [m]
                    cumulGndDist += gndDist #[m]
                    flMeter =  fl * 100 * m.ft2Meter #[m]
                    accFF = (nxt['descentFF']/60 - fuelFlowSec)/time #fuel flow rate of change
                    consumedFuel = fuelFlowSec*time + 0.5*accFF*(time**2) #same principle as the movement eq.
                    cumulConsumedFuel += consumedFuel #kg
                    descSA [i] = (nxt['fl'], nxt['descentNom']/60, -cumulTime, -cumulDist, -dist, 
                    gama, -gndDist, -cumulGndDist, flMeter, nxt['descentFF']/60,
                    -consumedFuel, -cumulConsumedFuel) 
                except Exception as e:
                    print("Exception: ", e)
                    #pdb.set_trace()
        #pdb.set_trace()
        return descSA
    def arrival(self, engine, noEngines, destinationICAO, year):
        """
        Args:
            engine (str): Aircraft engine model
            noEngines (int): Aircraft's number of engines 
            destinationICAO (str): Destination airport ICAO
            year(int): Year when the data was collected
        
        :returns:
            arrivalSA(rocdPTF): Arrival phase comprising approach, landing and taxi-in

        """
        arrivalSA = np.zeros(2, dtype = dt.rocdPTF)
        #Approach + landing
        approachLandTime = self.aircraftDefaultSA['timeSec'][self.aircraftDefaultSA['phase'] == 'approach'][0] #approach default time
        cumulTime = approachLandTime
        approachLandFuel = self.engineLTOSA['fuelApproach'][self.engineLTOSA['engineId'] == engine][0] #fuel rate [kg/sec./engine]
        fuelFlow = noEngines * approachLandFuel
        consumedApproachLandFuel = approachLandTime * fuelFlow
        cumulConsumedFuel = consumedApproachLandFuel
        arrivalSA[0] = (0, 0, cumulTime, 0, 0, 0, 0, 0, 0, fuelFlow,
                consumedApproachLandFuel, cumulConsumedFuel)
        #Taxi in
        taxiInTime = self.airportTaxiTimeSA['taxiIn' + str(year)][self.airportTaxiTimeSA['icaoAirport'] == destinationICAO][0]
        cumulTime += taxiInTime
        taxiInFuel = self.engineLTOSA['fuelTaxi'][self.engineLTOSA['engineId'] == engine][0] #fuel rate [kg/sec./engine]  
        fuelFlow = noEngines * taxiInFuel
        consumedTaxiInFuel = taxiInTime * fuelFlow 
        cumulConsumedFuel += consumedTaxiInFuel
        arrivalSA[1] = (0, 0, cumulTime, 0, 0, 0, 0, 0, 0, fuelFlow,
                consumedTaxiInFuel, cumulConsumedFuel)
        return arrivalSA
    def interpolCruise(self, rocdSA, fs, cruiseDist):
        m = CM.measures()
        fl = fs[1]['fl']
        flMeter =  fl * 100 * m.ft2Meter #[m]
        #calculate the total amount of time and fuel consumed
        r = rocdSA[rocdSA['fl'] == fl] #rocd for the fl
        jetStream = fs[1]['windSpeed']*fs[1]['intensity'] if fs[1]['fl'] > 360 else 0
        if len(r) > 0: #has the fl
            cruiseTAS = r['cruiseTAS'] + jetStream
            time = cruiseDist/((r['cruiseTAS'] + jetStream)* m.kntKmh * 1000/3600) #how long does it take to cover the cruiseDist
            fuelFlowSec =  r[self.ff ] /60 #fuel flow for the cur. fl [kg/sec] 
        else: #the fl needs to be interpol.
            try:
                upperFL = rocdSA['fl'][rocdSA['fl'] > fl][0]
                lowerFL = rocdSA['fl'][rocdSA['fl'] < fl][-1]
                upperTAS = rocdSA['cruiseTAS'][rocdSA['fl'] == upperFL][0]
                lowerTAS = rocdSA['cruiseTAS'][rocdSA['fl'] == lowerFL][0]
                cruiseTAS = np.interp(fl, [upperFL, lowerFL], [lowerTAS, upperTAS]) +  jetStream
                time = cruiseDist/(cruiseTAS * m.kntKmh * 1000/3600) #how long does it take to cover the cruiseDist
                upperFF = rocdSA[self.ff][rocdSA['fl'] == upperFL][0]
                lowerFF = rocdSA[self.ff][rocdSA['fl'] == lowerFL][0]
                fuelFlowSec = np.interp(fl, [lowerFL, upperFL], [lowerFF, upperFF])/60 #fuel flow for the cur. fl [kg/sec] 
            except:
                print(fs[1]['model'], fl, rocdSA)
                #pdb.set_trace()
        cumulConsumedFuel = time * fuelFlowSec
        cruiseSA = np.zeros(1, dtype = dt.rocdPTF)
        cruiseSA[0] = (fl, 0, time, cruiseDist, cruiseDist, 
                0 , cruiseDist, cruiseDist, flMeter, fuelFlowSec,
                cumulConsumedFuel, cumulConsumedFuel)
        return cruiseSA
    def normalClimb(self, climbSA, departureSA): #returns added time and fuel after climbout FL30
        """
        Args:
            climbSA (rocdPTF):
            departureSA (rocdPTF): 

        :returns:
            normalClimbSA(rocdPTF)
        """

        fl = departureSA['fl'][-1] #climb out fl30
        deptTime = departureSA['cumulTime'][-1] #dep. time 
        depCumulConsumedFuel = departureSA['cumulConsumedFuel'][-1] #dep. cumul. cons. fuel
        time = climbSA['cumulTime'][climbSA['fl'] == fl] #climb cumul. time @fl
        cumulConsumedFuel = climbSA['cumulConsumedFuel'][climbSA['fl'] == fl] #climb cumul. cons. fuel @fl
        climbSA30 = climbSA[climbSA['fl'] > fl]
        #size = len(climbSA30) #size of the array
        #normalClimbSA = np.zeros(size, dt.rocdPTF) #init. the array with zeros
        normalClimbSA = copy.deepcopy(climbSA30) #init. the array with climbSA start. @fl40
        i = 0
        for nxt in climbSA30: #interpol. through the PFT data struct.
            normalClimbSA[i]['cumulTime']  = nxt['cumulTime'] - time + deptTime #
            normalClimbSA[i]['cumulConsumedFuel'] = nxt['cumulConsumedFuel'] - cumulConsumedFuel + depCumulConsumedFuel  #cumul. consum. fuel @fl30
            i += 1
        return normalClimbSA
    def normalCruise(self, cruiseSA, normalClimbSA): #returns added points, time and fuel for cruise
        climbTime = normalClimbSA['cumulTime'][-1] #climb cumul. time 
        climbCumulConsumedFuel = normalClimbSA['cumulConsumedFuel'][-1] #climb cumul. cons. fuel
        climbCumulGndDist = normalClimbSA['cumulGndDist'][-1] #climb cumul. gnd. dist.
        normalCruiseSA = np.zeros(2, dtype = dt.rocdPTF)
        #Cruise start 
        normalCruiseSA[0] = normalClimbSA[-1] #init. 1st elem. w/ normalClimbSA
        normalCruiseSA[0]['fuelFlowSec'] = cruiseSA[0]['fuelFlowSec'] #update w/ fuel flow from
        #Cruise end
        normalCruiseSA[1] = cruiseSA[0] #init. w/ cruiseSA 1st elem.
        normalCruiseSA[1]['cumulTime'] += climbTime
        normalCruiseSA[1]['cumulConsumedFuel'] += climbCumulConsumedFuel
        normalCruiseSA[1]['cumulGndDist'] += climbCumulGndDist
        return normalCruiseSA
    def normalDescent(self, descentSA, normalCruiseSA): #returns added time and fuel for descent until FL 30
        cruiseTime = normalCruiseSA['cumulTime'][-1] #dep. time 
        cruiseCumulConsumedFuel = normalCruiseSA['cumulConsumedFuel'][-1] #dep. cumul. cons. fuel
        cruiseCumulGndDist = normalCruiseSA['cumulGndDist'][-1] #cruise cumul. gnd. dist @fl
        descSA30 = descentSA[descentSA['fl'] >= 30]
        size = len(descSA30) #size of the array
        normalDescSA = copy.deepcopy(descSA30) #init. the array with descentSA until @fl40
        i = 0
        for nxt in descSA30: #interpol. through the PFT data struct.
            normalDescSA[i]['cumulTime']  = nxt['cumulTime'] + cruiseTime #
            normalDescSA[i]['cumulConsumedFuel'] = nxt['cumulConsumedFuel'] + cruiseCumulConsumedFuel  #cumul. consum. fuel @fl30
            normalDescSA[i]['cumulGndDist'] = nxt['cumulGndDist'] + cruiseCumulGndDist  
            i += 1
        #pdb.set_trace()
        return normalDescSA
    def normalArrival(self, arrivalSA, normalDescentSA, cumulGndDist): #returns added time and fuel for arrival+landing and taxi-in
        time = normalDescentSA['cumulTime'][-1] #descent to fl30
        cumulConsumedFuel = normalDescentSA['cumulConsumedFuel'][-1]
        normalArrivalSA = np.zeros(4, dtype = dt.rocdPTF) #init. normalArrivalSA w/ zeros
        #Approach + landing start
        normalArrivalSA[0] = normalDescentSA[-1] #init. 1st elem. w/ normalDescentSA last elem. 
        normalArrivalSA[0]['fuelFlowSec'] = arrivalSA[0]['fuelFlowSec'] #update w/ fuel flow from approach
        #Approach + landing end 
        normalArrivalSA[1] = arrivalSA[0] #init. w/ arrivalSA 1st elem. 
        normalArrivalSA[1]['cumulTime'] += time
        normalArrivalSA[1]['cumulConsumedFuel'] += cumulConsumedFuel
        normalArrivalSA[1]['cumulGndDist'] += cumulGndDist #??? += / =
        normalArrivalSA[1]['fuelFlowSec'] = arrivalSA[0]['fuelFlowSec'] #update w/ fuel flow from approach
        #Taxi-in start
        normalArrivalSA[2] = normalArrivalSA[1] #init. w/ normalArrivalSA previous elem.
        normalArrivalSA[2]['fuelFlowSec'] = arrivalSA[1]['fuelFlowSec'] #update w/ fuel flow from taxi-in
        #Taxi-in end
        normalArrivalSA[3] = arrivalSA[1] #init. w/ arrivalSA 2nd elem.
        normalArrivalSA[3]['cumulTime'] += time
        normalArrivalSA[3]['cumulConsumedFuel'] += cumulConsumedFuel
        normalArrivalSA[3]['cumulGndDist'] += cumulGndDist #??? += / =
        return normalArrivalSA
  