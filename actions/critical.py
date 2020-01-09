
def flightMaint(fs):
    maintFlight = fs[fs['flight'] == 'm'] 
    airp = maintFlight['origin'][0]
    startInt = maintFlight['depInt'][0]
    criticalFligh = fs[(fs['destination'] == airp) & (fs['altArrInt'] <= startInt)][-1]
    return criticalFligh


