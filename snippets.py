            #flightSchedule[flightSchedule['delay'] > 0] #filtering
            #np.sort(flightSchedule, order = 'depInt') #ascend sort
            #np.sort(flightSchedule, order = 'depInt')[::-1] #descend sort
            #pprint(flightSchedule[['idFlight', 'origin']]) # print columns
            #infDic['A318#33']['cont'][0]['idFlight'] #rotation continuity flights
            #flightPair = flightSchedule[(flightSchedule['flight'] == cur['flight']) | (flightSchedule['flight'] == nxt['flight'])] #keep data as structured array
            # for iD in infDic:
                #print(infDic[iD].get('cont',None)) #get the cont. infeas.
            #y = len(tmpFlightSchedule)    
            #flightSchedule[0:y] = tmpFlightSchedule # copy an array to part of an array
            #for flight in np.nditer(flightArray[flightArray['flight'] != b'm']): #exclude maintenance
            #self.distSA['tripTypeInt'][self.distSA['tripType'] == 'D']= 1 #define column then criteria
            #idFlight = flight[0][:-8] #remove the 8 last elem.
            #d['word'] = [d['word'],'something'] #not sure if it is usefull
            #reversed_arr = arr[::-1] #reverse array
            #list[1:] get everything from the list except the first element
            #int('11111111', 2) convert base-2 binary number string to int
            #import os; os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2" supress warnings
            #res = [val for key, val in test_dict.items() if search_key in key] find key by keyword

            # orig_stdout = sys.stdout
            # f = open('out.txt', 'w')
            # sys.stdout = f
            # import pprint
            # # Prints the nicely formatted dictionary
            # pprint.pprint(airportDic)
            # sys.stdout = orig_stdout
            # f.close()

            # List all python (.py) files in the current folder and put them as __all__ variable in __init__.py

            # from os.path import dirname, basename, isfile, join
            # import glob
            # modules = glob.glob(join(dirname(__file__), "*.py"))
            # __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
            # np.array(np.meshgrid([-1, 0, 60, 780, 840, 900], [-1, 0, 600, 660, 720, 780])).T.reshape(-1,2)
            # np.array(np.meshgrid(*flightRanges.values())).T.reshape(-1,len(flightRanges))
            # product between a set of vectors
            # list(set(temp1) - set(temp2)) diff. between two lists