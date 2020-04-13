#TODO
#Define the dfs class
class dfs:
    def __init__(self, data, solution):
        self.data = data
        self.solution = solution

    def dfs(self, visited, graph, node):
        if node not in visited: #hard constraint
            visited.append(node)
            print(node)    
            #pdb.set_trace()
            for neighbour in graph[node]:
                prevArr = self.data.depARR[node][1] 
                nxtDep = self.data.depARR[neighbour][0]
                if prevArr + 30 <= nxtDep:
                    return self.dfs(visited, graph, neighbour)
                else:
                    try:
                        for delay in self.data.domains[neighbour][1]:
                            if (prevArr + 30 <= nxtDep + delay):
                                self.solution[neighbour] = delay
                                self.data.depARR[neighbour][0] += delay
                                self.data.depARR[neighbour][1] += delay
                                return self.dfs(visited, graph, neighbour)
                    except:
                        #backtrack
                        #pdb.set_trace()
                        index = self.data.flightSchedule.index(node)
                        return index
        return -1