class aircraft:
    aircraft =""
    model = ""
    family = ""
    F = -1
    B = -1
    E = -1
    rangeHours = -1
    hourOperatingCost = -1
    turnAround = -1
    transitTime = -1
    originAirport = ""
    maintAirport = ""
    maintStartDate = ""
    maintStartTime = ""
    maintStartInt = -1
    maintEndDate = ""
    maintEndTime = ""
    maintEndInt = -1
    maintDuration = -1
    
class airport:
    airport = ""
    idAirport = -1
    depArr = ""
    capDep = -1
    capArr = -1
    noDep = -1
    noArr = -1
    startTime = ""
    startInt = -1
    endTime = ""
    endInt = -1

class altAircraft:
    aircraft = ""
    startDate = ""
    startTime = ""
    startInt = -1
    endDate = ""
    endTime = ""
    endInt = -1

class altAirport:
    airport = ""
    startDate = ""
    startTime = ""
    startInt = -1
    endDate = ""
    endTime = ""
    endInt = -1
    capDep = -1
    capArr = -1
        
class altFlight:
    idAltFlight = -1
    depDateAltFligth = ""
    delayAltFlight = 0
        
class config:
    startDate = 0
    startTime = 0
    startInt = -1
    endDate = 0
    endTime = 0
    endInt = -1
    delayFdConfig = -1
    delayFcConfig = -1
    delayFiConfig = -1
    delayBdConfig = -1
    delayBcConfig = -1
    delayBiConfig = -1
    delayEdConfig = -1
    delayEcConfig = -1
    delayEiConfig = -1
    cancelOutboundFdConfig = -1
    cancelOutboundFcConfig = -1
    cancelOutboundFiConfig = -1
    cancelOutboundBdConfig = -1
    cancelOutboundBcConfig = -1
    cancelOutboundBiConfig = -1
    cancelOutboundEdConfig = -1
    cancelOutboundEcConfig = -1
    cancelOutboundEiConfig = -1
    cancelInboundFdConfig = -1
    cancelInboundFcConfig = -1
    cancelInboundFiConfig = -1
    cancelInboundBdConfig = -1
    cancelInboundBcConfig = -1
    cancelInboundBiConfig = -1
    cancelInboundEdConfig = -1
    cancelInboundEcConfig = -1
    cancelInboundEiConfig = -1
    


class dist:
    originAirport = ""
    destinationAirport = ""
    dist = -1
    tripType = "" # I C D
    tripTypeInt = -1 # 3 2 1
    space = -1
    
class flight:
    idFlight = -1
    origin = ""
    destination = ""
    depTime = ""
    depInt = 0
    arrTime = ""
    arrInt = 0
    arrNextDay = 0
    previous = 0
    
class itinerary:
    idItinerary = -1
    typeItinerary = "" # A R
    typeItineraryInt = -1
    price = -1
    count = -1
    idFlight = -1
    date = ""
    cabin = "" # F B E
    cabinInt = -1 # 3 2 1
    
class rotation:
    idFlight = -1
    date = ""
    aircraft = ""
    
class flightProfile:
    fl = -1
    climbFuel = -1
    cruiseFuel = -1
    descentFuel = -1
    
class fRA(flight, rotation, aircraft, altFlight, altAircraft):
    dayInt = -1
    depDateTime = ""
    arrDateTime = ""

    altDepDateTime = ""
    altArrDateTime = ""
    altDepInt = 0
    altArrInt = 0
    depAirportInt = -1 # airport id
    arrAirportInt = -1 # airport id
    altAircraft = 0 # aircraft broken period
    delay = 0
    maxDelay = -1 # max delay depending on the type of itinerary (A/R) and type of flight (I/C/D)
    newFlight = 0 # the flight is created a  new number is given
    cancelFlight = 0

class iFRAD(itinerary, fRA, dist):
    index = -1
    altTripTypeInt = -1  
    altCabinInt = -1
    cancelItinerary = 0