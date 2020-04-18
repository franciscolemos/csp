def saveARP(rotation):
    pass

def saveAirportCap(flightSchedule, airportCap):
    for flight in flightSchedule[flightSchedule['flight'] != '']:
        #update airp. dep. cap.
        index = int(flight['altDepInt']/60)
        airportCap[flight['origin']][index]['noDep'] += 1
        #update airp. arr. cap.
        index = int(flight['altArrInt']/60)
        airportCap[flight['destination']][index]['noArr'] += 1

def savePRP(itineraries):
    pass
