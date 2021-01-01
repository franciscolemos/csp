#!/usr/bin/env python
#
# geo.py is a python module with no dependencies on extra packages,
# providing some convenience functions for working with geographic
# coordinates
#
# Copyright (C) 2010  Maximilian Hoegner <hp.maxi@hoegners.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

### Part one - Functions for dealing with points on a sphere ###
import math

EARTH_RADIUS = 6370000.
MAG_LAT=82.7
MAG_LON=-114.4

direction_names = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
directions_num = len(direction_names)
directions_step = 360./directions_num

def xyz(lat,lon,r=EARTH_RADIUS):
	""" Takes spherical coordinates and returns a triple of cartesian coordinates """
	x = r*math.cos(math.radians(lat))*math.cos(math.radians(lon))
	y = r*math.cos(math.radians(lat))*math.sin(math.radians(lon))
	z = r*math.sin(math.radians(lat))
	return x,y,z

def dot(p1,p2):
	""" Dot product of two vectors """
	return p1[0]*p2[0]+p1[1]*p2[1]+p1[2]*p2[2]

def cross(p1,p2):
	""" Cross product of two vectors """
	x = p1[1]*p2[2]-p1[2]*p2[1]
	y = p1[2]*p2[0]-p1[0]*p2[2]
	z = p1[0]*p2[1]-p1[1]*p2[0]
	return x,y,z

def determinant(p1,p2,p3):
	""" Determinant of three vectors """
	return dot(p1,cross(p2,p3))

def normalize_angle(angle):
	""" Takes angle in degrees and returns angle from 0 to 360 degrees """
	cycles = angle/360.
	normalized_cycles = cycles - math.floor(cycles)
	return normalized_cycles*360.

def sgn(x):
	""" Returns sign of number """
	if x==0: return 0.
	elif x>0: return 1.
	else: return -1.

def angle(v1,v2,n=None):
	#Returns angle between v1 and v2 in degrees. n can be a vector that points to an observer who is looking at the plane containing v1 and v2. This way, you can get well-defined signs.
    if n==None:
        n=cross(v1,v2)

    prod = dot(v1,v2) / math.sqrt( dot(v1,v1) * dot(v2,v2) )
    if prod > 1 :
         prod=1.0 # avoid numerical problems for very small angles
    rad = sgn(determinant(v1,v2,n)) * math.acos( prod )
    deg = math.degrees(rad)
    return normalize_angle(deg)

def great_circle_angle(p1,p2,p3):
	""" Returns angle w(p1,p2,p3) in degrees. Needs p1 != p2 and p2 != p3. """
	n1=cross(p1,p2)
	n2=cross(p3,p2)
	return angle(n1,n2,p2)

def distance(p1,p2,r=EARTH_RADIUS):
	""" Returns length of curved way between two points p1 and p2 on a sphere with radius r. """
	return math.radians(angle(p1,p2)) * r

def direction_name(angle):
	""" Returns a name for a direction given in degrees. Example: direction_name(0.0) returns "N", direction_name(90.0) returns "O", direction_name(152.0) returns "SSO". """
	index = int(round( normalize_angle(angle)/directions_step ))
	index %= directions_num
	return direction_names[index]

magnetic_northpole=xyz(MAG_LAT,MAG_LON)
geographic_northpole=xyz(90,0)

### Part two - A tolerant parser for position strings ###
