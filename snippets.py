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
            # itineraryLine = list(filter(None, itineraryLine)) # clean empty values from list
            # [e for l in [(0, 2640), (900, 900, 660, 180)] for e in l] flatten a list of tuples
            # df = pd.DataFrame(table)
            # df.sort_values(by= [0, 1], ascending=[False, True])
            # np.concatenate(self.solutionARP).ravel() flatten list of numpy arrays
            #  python -m site --user-site get python packages
            # np.setdiff1d(a, b) diff. between two numpy arrays
            # found_index = np.in1d(input_series, val).nonzero()[0] new_array = numpy.delete(input_series, found_index)
     
            # flightOrder =  collections.OrderedDict(sorted(self.flightDic.items())) order dictionary
            # lastFlight = flightOrder.popitem()[0]
            #numpy.savetxt("foo.csv", a, delimiter=",")

            #[print(key, value) for key, value in flightRanges.items()] Print a dictionary line by line using List Comprehension
            #[value for value in arp.solutionARP.values()]
            #solutionARP =  np.concatenate([value for value in arp.solutionARP.values()]).ravel()

            # def evaluate(self):
            #     fitness = []
            #     for individual in self.pop:
            #         rotation = copy.deepcopy(self.rotationOriginal) #keep a copy of the original because of new rotation
            #         #import pdb; pdb.set_trace()
            #         solution.newRotation(individual[0], rotation[self.index:]) #add the combo to the rotation
            #         rotationCopy = copy.deepcopy(rotation[rotation['cancelFlight'] != 1]) #only flights not cancelled in the copy
            #         rotationCopy = np.sort(rotationCopy, order = 'altDepInt')
            #         sizeInfCont = len(feasibility.continuity(rotationCopy))
            #         sizeInfTT = len(feasibility.TT(rotationCopy))
                
            #         noInf = sizeInfCont + sizeInfTT
            #         noCancel = sum([i for i in individual[0] if i == -1])
            #         delay = sum([i for i in individual[0] if i != -1])
            #         fitness.append([noInf, noCancel, delay])
            #     return fitness

            # offspring[::2] group every 2 elem. start at index 0 pick first
            # offspring[1::2] group every 2 elem. start at index 1 pick first

            # print("Before")
            # for ind in self.pop:
            #     print(ind, ind.fitness)

            # self.pop.sort(key = lambda x: x.fitness, reverse =True)
            
            # print("After")
            # for ind in self.pop:
            #     print(ind, ind.fitness)

            # print("init. sol.")
            # fits = [ind.fitness.values for ind in self.pop]
            # pprint.pprint(self.pop)
            # pprint.pprint(fits)