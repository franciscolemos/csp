# Using a Python dictionary to act as an adjacency list
import pdb
import repositories.data as data

solution = {
    '724001/03/08':[],
    '724301/03/08':[],
    '286601/03/08':[],
    '286701/03/08':[],
    '530301/03/08':[],
    '530002/03/08':[],
    'm':[],
    '736602/03/08':[],
    '736902/03/08':[],
    '737002/03/08':[]
}

visited = [] # Array to keep track of visited nodes.

def dfs(visited, graph, node):
    if node not in visited: #hard constraint
        visited.append(node)
        print(node)    
        #pdb.set_trace()
        for neighbour in graph[node]:
            prevArr = data.depARR[node][1] 
            nxtDep = data.depARR[neighbour][0]
            if prevArr + 30 <= nxtDep:
                return dfs(visited, graph, neighbour)
            else:
                try:
                    for delay in data.domains[neighbour][1]:
                        if (prevArr + 30 <= nxtDep + delay):
                            solution[neighbour] = delay
                            data.depARR[neighbour][0] += delay
                            data.depARR[neighbour][1] += delay
                            return dfs(visited, graph, neighbour)
                except:
                    #backtrack
                    #pdb.set_trace()
                    index = data.flightSchedule.index(node)
                    return index
    return -1

#define the critical flight

index = 0
while(index != -1):
    startFlight = data.flightSchedule[index] #starting flight to start the dfs
    index = dfs(visited, data.graphFs,startFlight)
    #cancel the flightSchedule[index]
    #save the partial solution
    #define the critical flight
    #delete the loop files
    #create new solution from the flightSchedule
    pdb.set_trace()
    print(solution)