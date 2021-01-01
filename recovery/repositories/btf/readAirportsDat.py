"""
readAirportsDat.py
===================
This module reads te CSV files with the airport's coordinates, taxi time, aircraft thrust and time default values, aircraft engines, aircraft fuel flow for every phase
"""

import os
import numpy as np
from numpy import genfromtxt
from recovery.dal.classesDtype import dtype as dt


class airport:
    def __init__(self):
        self.path2File = {'airports': './recovery/btf/dataSets/airports.dat' #geo. coord. IAT code
            , 'airportTaxiTime': './recovery/btf/dataSets/aircraftData/airportTaxiTime.csv'
            , 'aircraftDefault': './recovery/btf/dataSets/aircraftData/aircraftDefault.csv'
            , 'aircraftEngine': './recovery/btf/dataSets/aircraftData/aircraftEngine.csv'
            , 'engineLTO': './recovery/btf/dataSets/aircraftData/engineLTO.csv'       
        }
        self.airportsDatSA = []
        self.airportTaxiTimeSA = []
        self.aircraftDefaultSA = []
        self.aircraftEngineSA = []
        self.engineLTOSA = []
        self.read2SA()

    def read2SA(self):
        """
        This method retrieves the airport's coordinates, taxi time, aircraft thrust and time default values, aircraft engines, aircraft fuel flow for every phase
        """
        self.airportsDatSA = genfromtxt(self.path2File['airports'], delimiter=',', deletechars = '"', dtype = dt.dtypeAirp, encoding='utf8')
        self.airportTaxiTimeSA = genfromtxt(self.path2File['airportTaxiTime'], delimiter=',', dtype = dt.airportTaxiTime, encoding='utf8')
        self.aircraftDefaultSA = genfromtxt(self.path2File['aircraftDefault'], delimiter=',', dtype = dt.aircraftDefault, encoding='utf8')
        self.aircraftEngineSA = genfromtxt(self.path2File['aircraftEngine'], delimiter=',', dtype = dt.aircraftEngine, encoding='utf8')
        self.engineLTOSA = genfromtxt(self.path2File['engineLTO'], delimiter=',', dtype = dt.engineLTO, encoding='utf8')