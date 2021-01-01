import math
import pdb
import recovery.actions.btf.geo
import recovery.repositories.btf.classesMeasures as CM

class headDist:
    def heading(self, coord1, coord2):
        if (type(coord1) != tuple) or (type(coord2) != tuple):
            raise TypeError("Only tuples are supported as arguments")
        lat1 = math.radians(coord1[0])
        lat2 = math.radians(coord2[0])
        diffLong = math.radians(coord2[1] - coord1[1])
        x = math.sin(diffLong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
                * math.cos(lat2) * math.cos(diffLong))
        initial_bearing = math.atan2(x, y)

        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        return compass_bearing
    def haversine(self, coord1, coord2):
        m = CM.measures()
        R = m.earthRadius
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        phi1, phi2 = math.radians(lat1), math.radians(lat2) 
        dphi       = math.radians(lat2 - lat1)
        dlambda    = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + \
            math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))
