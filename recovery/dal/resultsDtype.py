import numpy as np

resultsDtype = np.dtype([
('dateTime', np.unicode, 15)
#, ('time', np.unicode, 13)
, ('dataInstance', np.unicode, 13)
, ('checkAircraftBreakdownPeriod', np.int16)
, ('checkAircraftCapacity', np.int16)
, ('checkAircraftCreation', np.int16)
, ('checkAircraftSwap', np.int16)
, ('checkAirportCapacity', np.int16)
, ('checkCancellationofCreatedRotation', np.int16)
, ('checkFixedFlights', np.int16)
, ('checkFlight', np.int16)
, ('checkItinerary', np.int16)
, ('checkPassengerReac', np.int16)
, ('checkRotation', np.int16)
])