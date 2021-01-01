import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import pandas as pd
import numpy as np
from numpy import genfromtxt
from recovery.dal.btf.classesDtype import dtype as dt
import pdb

#path2File = "C:\\Users\\Paisagem\\Google DRIVE\\QMUL\\THESIS\\3rd year\\paperBadaEEA\\cdgA320Bcn\\"
path2File = "C:\\Users\\chico\\repos\\franciscolemos\\BTF\\airportSpaceDist\\plots"
def dicSet(fs, cumulPhaseSA):
    time = cumulPhaseSA['cumulTime'] /60
    gndDist = cumulPhaseSA['cumulGndDist'] / 1000
    ffMin = cumulPhaseSA['fuelFlowSec'] * 60
    #'H:\\QMUL\\THESIS\\3rd year\\paperBadaEEA\\figures\\'
    
    decorFuelFlow = [{'x':time, 'y':ffMin,
        'legend': fs[1]['model'] + ' flying from ' + fs[1]['origin'] + ' to ' + fs[1]['destination'] + ' dist. = ' + str(int(fs[1]['physDist'])) + ' km',
        'legendLoc':0,
        'xLabel':'Time [min]',
        'xRange':np.arange(min(time), max(time)+10, 15 ),
        'yLabel':'Fuel flow [kg/min]', 
        'yRange':np.arange(0, max(ffMin) + 15, 50),
        'graphTitle':'Fuel flow vs. time'}] #,
    graph(decorFuelFlow)
        
    decorFuelFlow = [{'x':time, 'y':cumulPhaseSA['fl'],
        'legend': "Altitude profile",
        'legendLoc':0,
        'xLabel':'Time [min]', 
        'xRange':np.arange(min(time), max(time)+10, 15 ),
        'yLabel':'Altitude [FL]', 
        'yRange':np.arange(0, max(cumulPhaseSA['fl']) + 50, 50),
        'graphTitle':'Altitude vs. time'}]#,
    graph(decorFuelFlow)

    decorFuelFlow = [{'x':time, 'y':gndDist,
        'legend': 'Ground distance',
        'legendLoc':0,
        'xLabel':'Time [min]',
        'xRange':np.arange(min(time), max(time)+10, 15 ),
        'yLabel':'Distance [Km]', 
        'yRange':np.arange(0, max(gndDist)+50, 100 ),
        'graphTitle':'Ground distance vs. time'}]
    graph(decorFuelFlow)
    
    pdb.set_trace()

def oriAircDestDic(fs, cumulPhaseSA):
    pdb.set_trace()
    #if(fs[1]['origin'] == dic['origin']) & (fs[1]['model'] == dic['model']) & (fs[1]['destination'] == dic['destination']):
    oriAircDest = fs[1]['origin'] + fs[1]['model'] + fs[1]['destination']
    oriAircDestSA = genfromtxt('.\\repositories\\' + oriAircDest + '_altGndDist.csv', delimiter=',', dtype = dt.flightCdgBcn, skip_header = 1)
    #else:
        #return

    decorFuelFlow = [{}] #this is slightly stupid
    timeOriAircDest = oriAircDestSA['time'] #get the time vector from oriAircDestSA
    time = cumulPhaseSA['cumulTime'] /60

    altOriAircDest = oriAircDestSA['fl'] #alt. profile for flight CDG to BCN w/ A320
    decorFuelFlow = [{'x':[time, timeOriAircDest], #time for the 2 series
        'y':[cumulPhaseSA['fl'], altOriAircDest], #altitude profile for the 2 series
        'graphTitle':'Comparison between Flightaware and BTF for altitude vs time',
        'legend': ["Altitude profile for BTF", "Altitude profile for Flightware"],
        'legendLoc':0,
        'xLabel':'Time [min]', 
        'xRange':np.arange(min(time)-15, max(time)+10, 15 ),
        'yLabel':'Altitude [FL]', 
        'yRange':np.arange(-50, max(cumulPhaseSA['fl']) + 50, 50),
        'graphTitle':'Altitude vs. time',
        'path': path2File + oriAircDest + '_alt.png'}]
    graph2Series(decorFuelFlow)

    gndDistOriAircDest = oriAircDestSA['gndDist'] #ground dist. for flight CDG to BCN w/ A320
    gndDist = cumulPhaseSA['cumulGndDist'] / 1000
    decorFuelFlow = [{'x':[time, timeOriAircDest], #time for the 2 series
        'y':[gndDist, gndDistOriAircDest], #ground dist. for the 2 series
        'graphTitle':'Comparison between Flightaware and BTF for ground distance vs time',
        'legend': ["Ground distance for BTF", "Ground distance for Flightware"],
        'legendLoc':0,
        'xLabel':'Time [min]',
        'xRange':np.arange(min(time)-15, max(time)+10, 15 ),
        'yLabel':'Distance [Km]', 
        'yRange':np.arange(-100, max(gndDist)+50, 100 ),
        'graphTitle':'Ground distance vs. time',
        'path':path2File + oriAircDest + '_gndDist.png'}]
    graph2Series(decorFuelFlow)

def dicCdgA320Bcn(fs, cumulPhaseSA):
    if(fs[1]['origin'] == 'CDG') & (fs[1]['model'] == 'A320') & (fs[1]['destination'] == 'BCN'):
    	cdgA320BcnSA = genfromtxt('./dataSets/flightaware/cdgA320Bcn_AltGnd.csv', delimiter=',', dtype = dt.flightCdgBcn, skip_header = 1)
        #cdgA320BcnSA = pd.read_csv('.\\repositories\\cdgA320Bcn_AltGnd.csv', header = None, delimiter=',')
    else:
        return
    #https://uk.flightaware.com/live/flight/AFR1148/history/20191023/0520Z/LFPG/LEBL
    #https://uk.flightaware.com/live/flight/AFR1148/history/20191023/0520Z/LFPG/LEBL/tracklog
    decorFuelFlow = [{}] #this is slightly stupid
    timeCdgA320Bcn = cdgA320BcnSA['time']
    time = cumulPhaseSA['cumulTime'] /60

    altCdgA320Bcn = cdgA320BcnSA['fl'] #alt. profile for flight CDG to BCN w/ A320
    decorFuelFlow = [{'x':[time, timeCdgA320Bcn], #time for the 2 series
        'y':[cumulPhaseSA['fl'], altCdgA320Bcn], #altitude profile for the 2 series
        'graphTitle':'Comparison between Flightaware and BTF for altitude vs time',
        'legend': ["Altitude profile for BTF", "Altitude profile for Flightware"],
        'legendLoc':0,
        'xLabel':'Time [min]', 
        'xRange':np.arange(min(time)-15, max(time)+10, 15 ),
        'yLabel':'Altitude [FL]', 
        'yRange':np.arange(-50, max(cumulPhaseSA['fl']) + 50, 50),
        'graphTitle':'Altitude vs. time',
        'path':path2File + 'altCdgA320Bcn_1.png'}]
    graph2Series(decorFuelFlow)

    gndDistCdgA320Bcn = cdgA320BcnSA['gndDist'] #ground dist. for flight CDG to BCN w/ A320
    gndDist = cumulPhaseSA['cumulGndDist'] / 1000
    decorFuelFlow = [{'x':[time, timeCdgA320Bcn], #time for the 2 series
        'y':[gndDist, gndDistCdgA320Bcn], #ground dist. for the 2 series
        'graphTitle':'Comparison between Flightaware and BTF for ground distance vs time',
        'legend': ["Ground distance for BTF", "Ground distance for Flightware"],
        'legendLoc':0,
        'xLabel':'Time [min]',
        'xRange':np.arange(min(time)-15, max(time)+10, 15 ),
        'yLabel':'Distance [Km]', 
        'yRange':np.arange(-100, max(gndDist)+50, 100 ),
        'graphTitle':'Ground distance vs. time',
        'path': path2File + 'gdnDistCdgA320Bcn_1.png'}]
    graph2Series(decorFuelFlow)

def graph2Series(decorSA):
    fig, axs = plt.subplots(nrows= len(decorSA), figsize=(15, 6))
    axs.set_title(decorSA[0]['graphTitle'])
    x = decorSA[0]['x']
    y = decorSA[0]['y']
    axs.plot(x[0], y[0], '-ok', markersize = 5, label = decorSA[0]['legend'][0], fillstyle = 'none')
    axs.plot(x[1], y[1], '-xk', markersize = 5, label = decorSA[0]['legend'][1])
    axs.set(xlabel=decorSA[0]['xLabel'], ylabel=decorSA[0]['yLabel'])
    axs.xaxis.set_ticks(decorSA[0]['xRange'])
    axs.yaxis.set_ticks(decorSA[0]['yRange'])
    axs.legend(loc = decorSA[0]['legendLoc'])
    axs.grid(linestyle = ':')
    plt.style.use('classic')
    plt.savefig(decorSA[0]['path'])
    plt.show()

def graph(decorSA):
    if len(decorSA) == 1:
        fig, axs = plt.subplots(nrows= len(decorSA))
        axs.set_title(decorSA[0]['graphTitle'])
        x = decorSA[0]['x']
        y = decorSA[0]['y']
        axs.plot(x, y, '-ok', markersize = 2.5, label = decorSA[0]['legend'])
        axs.set(xlabel=decorSA[0]['xLabel'], ylabel=decorSA[0]['yLabel'])
        axs.xaxis.set_ticks(decorSA[0]['xRange'])
        axs.yaxis.set_ticks(decorSA[0]['yRange'])
        axs.legend(loc = decorSA[0]['legendLoc'])
        axs.grid(linestyle = ':')
        plt.style.use('classic')
        plt.show()
    else:
        fig, axs = plt.subplots(nrows= len(decorSA))
        fig.tight_layout()
        i = 0
        for decor in decorSA:
            axs[i].set_title(decor['graphTitle'])
            x = decor['x']
            y = decor['y']
            axs[i].plot(x, y, '-ok', markersize = 2.5, label = decor['legend'])
            axs[i].set(xlabel=decor['xLabel'], ylabel=decor['yLabel'])
            axs[i].xaxis.set_ticks(decor['xRange'])
            axs[i].yaxis.set_ticks(decor['yRange'])
            axs[i].legend(loc = decor['legendLoc'])
            axs[i].grid(linestyle = ':')
            i += 1
        plt.style.use('classic')
        plt.subplots_adjust(left = 0.12, hspace = 0.67)
        plt.show()

def graphScatter(decorSA):
    if len(decorSA) == 1:
        fig, axs = plt.subplots(nrows= len(decorSA))
        axs.set_title(decorSA[0]['graphTitle'])
        x = decorSA[0]['x']
        y0 = decorSA[0]['y'][0]
        axs.plot(x, y0, 'o', markersize = 6, fillstyle = u'none', label = decorSA[0]['ySeries'][0])
        y1 = decorSA[0]['y'][1]
        axs.plot(x, y1, 'x', markersize = 5, label = decorSA[0]['ySeries'][1])
        axs.set(xlabel=decorSA[0]['xLabel'], ylabel=decorSA[0]['yLabel'])
        axs.xaxis.set_ticks(decorSA[0]['xRange'])
        axs.yaxis.set_ticks(decorSA[0]['yRange'])
        axs.legend(loc = decorSA[0]['legendLoc'])
        axs.grid(linestyle = ':')
        plt.style.use('seaborn-whitegrid')
        plt.show()
