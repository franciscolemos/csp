import numpy as np

class dtype:
    fmtDate = '%d/%m/%y'
    fmtTime = '%H:%M'
    
    #data type for the itinerary flight schedule
    dtypeItinFS= np.dtype([('flightIndex', np.uint8), ('flight', np.unicode, 13), ('cabin', np.int8), ('trip', np.int8), ('aircraft', np.unicode, 15),
        ('origin', np.unicode, 3 ), ('depInt', np.int16), ('altDepInt', np.int16), 
        ('destination', np.unicode, 3), ('arrInt', np.int16), ('altArrInt', np.int16), 
        ('previous', np.unicode, 5), ('cancelFlight', np.uint8), ('cancelItin', np.uint8)])
    #cabin
    cabinInt = {'F':3, 'B':2, 'E':1}
    cabin = {3:'F', 2:'B', 1:'E'}
    #dist
    distInt = {'I':3, 'C':2, 'D':1}
    dist = {3:'I', 2:'C', 1:'D'}
    #delays
    maxDelay = {'LNS':960, 'inboundDC':1080, '1':1380, '2':1680, 'inboundI':2160} #max. available delays
    #data type for the aircraft schedule flights
    dtypeAS = np.dtype([('flight', np.unicode, 13),('idFlight', np.unicode, 5), ('date', 'datetime64[D]' ), ('origin', np.unicode, 3 ), ('depInt', np.int16), ('altDepInt', np.int16), 
        ('destination', np.unicode, 3), ('arrInt', np.int16), ('altArrInt', np.int16), ('previous', np.unicode, 5), ('tt', np.int16),
        ('delay', np.int16), ('broken', np.int8), ('cancelFlight', np.uint8)])
    #data type for the flight schedule
    dtypeFS = np.dtype([('aircraft', np.unicode, 15), ('family', np.unicode, 15), ('flight', np.unicode, 13), 
        ('origin', np.unicode, 3 ), ('depInt', np.int16), ('altDepInt', np.int16),
        ('destination', np.unicode, 3), ('arrInt', np.int16), ('altArrInt', np.int16),
        ('previous', np.unicode, 5), ('tt', np.int16),
         ('cancelFlight', np.uint8)])
    #data type for flight schedule with dist.
    dtypeFSD = np.dtype([('aircraft', np.unicode, 15), ('family', np.unicode, 15), ('flight', np.unicode, 13), 
        ('origin', np.unicode, 3 ), ('dist', np.int16), ('physDist', np.float), ('timeDist', np.float)])
    #data type for chromFASA + solFS =  chromFSSolSA flight sched. 
    dtypeChromSol =  np.dtype([('flight', np.unicode, 13),
                    ('origin', np.unicode, 3 ), ('altDepInt', np.int16),
                    ('destination', np.unicode, 3), ('altArrInt', np.int16),
                    ('previous', np.unicode, 5), ('tt', np.int16),
                    ('sol', np.unicode, 13), ('cancelSol', np.unicode, 1)])
    #BADA PTF 
    PTF2CsvDic = {'A318':'A318.csv', 'A319':'A319.csv', 'A320':'A320.csv', 'A321':'A321.csv', 
                'A330':'A330.csv', 'A340':'A340.csv', 'B737300':'B737300.csv', 'B737400':'B737400.csv',
                'B737800':'B737800.csv', 'B737900':'B737900.csv', 'B747':'B747.csv',
                'B744':'B744.csv',
                'B777':'B777.csv',
                'B789':'B789.csv',
                'BAE200':'BAE200.csv', 'BAE300':'BAE300.csv', 'CRJ100':'CRJ100.csv', 'CRJ700':'CRJ700.csv',
                'ERJ135':'ERJ135.csv', 'ERJ145':'ERJ145.csv', 'F100':'F100.csv'}
    #BADA PTF
    aircraftPTF = np.dtype([('model', np.unicode, 13), ('casLoClimb', np.float), ('casHiClimb', np.float),
        ('casLoCruise', np.float), ('casHiCruise', np.float), ('casLoDescent', np.float), ('casHiDescent', np.float),
        ('machClimb', np.float), ('machCruise', np.float), ('machDescent', np.float), ('mlLo', np.float), ('mlNom', np.float),
        ('mlHi', np.float), ('maxAlt', np.int16), ('obs', np.unicode, 100)])
    #BADA PTF ROCD
    aircROCD = np.dtype([('fl', np.int16), ('cruiseTAS', np.int16), ('cruiseLo', np.float), ('cruiseNom', np.float), ('cruiseHi', np.float), 
        ('climbTAS', np.int16), ('climbLo', np.int16), ('climbNom', np.int16), ('climbHi', np.int16), ('climbFFNom', np.float),
        ('descentTAS', np.int16), ('descentNom', np.int16), ('descentFF', np.float)])

    #airports.dat
    dtypeAirp = np.dtype([('idAirport', np.int32), ('nameAirport',  object), ('cityAirport', object),
        ('countryAirport', np.unicode, 20), ('iataAirport', np.unicode, 3), ('icaoAirport', np.unicode, 4), 
        ('latitudeAirport', np.float), ('longitudeAirport', np.float), ('altitudeAirport', np.float), 
        ('timezoneAirport', np.float), ('dstAirport', np.unicode, 1), ('tzAirport', np.unicode, 30), 
        ('typeAirport', np.unicode, 10), ('sourceAirport', np.unicode, 15)])

    #dist. relation with flight levels for cruise altitude
    data = [(0, 180, [(498.79, 804.5,330, 130, 0.3), (804.5, 1206.75, 350, 140, 0.3), (1206.75, 14022.5, 370, 150, 0.2)]),
            (180, 360,   [(498.79, 804.5, 340, 135, -0.3), (804.5, 1206.75, 360, 150, -0.3), (1206.75, 14022.5, 380, 155, -0.2)])
            ]
    bearDistFl = np.array(data, dtype=[('lBound', np.float),
                                ('uBound', np.float),
                                ('response', [('lDist', np.float), ('uDist', np.float),
                                                ('fl', np.float), ('windSpeed', np.int16), ('intensity', np.float)], (3,))
                                ])
    #data from the European Environment Agency
    airportTaxiTime = np.dtype([('icaoAirport', np.unicode, 4), ('taxiOut2006', np.float), ('taxiOut2008', np.float),
        ('taxiIn2006', np.float), ('taxiIn2008', np.float)])
    aircraftDefault = np.dtype([('phase', np.unicode, 10), ('powerPerc', np.int16), ('timeSec', np.int16)])    
    aircraftEngine = np.dtype([('aircraft', np.object), ('engineId', np.unicode, 10), ('engineDesign', np.unicode, 20),
        ('noEngine', np.int8), ('model', np.unicode, 10), ('modelBADA', np.unicode, 10)])
    engineLTO = np.dtype([('engineId', np.unicode, 10), ('fuelTakeOff', np.float), ('fuelApproach', np.float), ('fuelTaxi', np.float), ('fuelClimb', np.float)])

    #record the flight on the diff. phases
    rocdPTF = np.dtype([('fl', np.int16), ('rocdRate', np.float), ('cumulTime', np.float), ('cumulDist', np.float), ('airDist', np.float), 
        ('gama', np.float), ('gndDist', np.float), ('cumulGndDist', np.float), ('flMeter', np.float), ('fuelFlowSec', np.float),
        ('consumedFuel', np.float), ('cumulConsumedFuel', np.float)])

    #cruise durat. relation with flight dist.
    durWB = {'m':0.053697949, 'b':10}
    durEB = {'m':0.063393412, 'b':10}

    #fligtaware data
    flightHistory = np.dtype([('idFlight', np.unicode, 20), #airc. + origin + dest.
                    ('model', np.unicode, 14),
                    ('idFlightaware', np.unicode, 20), ('date', np.unicode, 11),
                    ('aircraft', np.unicode, 14),
                    ('origin', np.unicode, 150), ('destination', np.unicode, 150), 
                    ('departure', np.unicode, 150),
                    ('arrival', np.unicode, 150), ('duration', np.unicode, 150),
                    ('durationInt', np.int32)
                    ])

    flightCdgBcn = np.dtype([('time', np.float),
                    ('fl', np.float), ('gndDist', np.float)])

    flightPlan = np.dtype([ ('key', np.unicode, 20), 
        ('origin', np.unicode, 3), ('model', np.unicode, 14), ('destination', np.unicode, 3),
        ('cumulTime', np.float), ('physDist', np.float), ('cumulConsumedFuel', np.float)])
    
    flightStats = np.dtype([ ('key', np.unicode, 20), 
        ('origin', np.unicode, 3), ('model', np.unicode, 14), ('destination', np.unicode, 3),
        ('physDist', np.float), 
        ('modelConsumedFuel', np.float), ('modelTime', np.float), 
        ('modelPercentile', np.float), ('modelRMSE', np.float),
        ('roadefTime', np.float), ('roadefPercentile', np.float), ('roadefRMSE', np.float),
        ('sampleSize', np.float), ('sampleMean', np.float), ('sampleMedian', np.float)
         ])
    
