import numpy as np
import json 

TEXT_COLOR_RED = "\033[31;1m"
TEXT_COLOR_GREEN = "\033[32;1m"
TEXT_COLOR_YELLOW = "\033[33;1m"
TEXT_COLOR_BLUE = "\033[34;1m"
TEXT_COLOR_MAGENTA = "\033[35;1m"
TEXT_COLOR_CYAN = "\033[36;1m"
TEXT_COLOR_WHITE = "\033[37;1m"
TEXT_COLOR_DEFAULT = "\033[0m"

def findCanonicalPattern(numberOfTeams, numberOfRounds): 
       
    x = numberOfRounds//2
    y = numberOfTeams//2
    z = 2    
    # Creates 3-dimensional array. For example, for 4 teams: x = 2, y = 3, z = 2. So E = [[[0,0],[0,0]],[[0,0],[0,0]],[[0,0],[0,0]]]
    E = np.zeros((x,y,z)) 
    
    for i in range(numberOfRounds//2): 
        
        E[i][0][:]=[numberOfTeams,i + 1]        # The first edge of a round is the last team (e.g. team 4) playing team i + 1 
        
        for k in range(numberOfTeams//2-1):      # Then to fill the last edges, use functions F1 and F2
            
            E[i][k+1][:]=[F1(i + 1, k + 1, numberOfTeams), F2(i + 1, k + 1, numberOfTeams)] 
         
    return(E) 

    
# Defines F1 used to find the canonical pattern   
def F1(i,k,numberOfTeams):
    
    if i + k < numberOfTeams:
        
        return(i + k)
        
    else:
        
        return(i + k - numberOfTeams + 1)
    
    
# Defines F2 used to find the canonical pattern     
def F2(i,k,numberOfTeams):
    
    if i - k > 0:
        
        return(i - k)
        
    else:
        
        return(i - k + numberOfTeams - 1)
        

# Defines function to get initial solution for Simulated Annealing
def getInitialSolution(numberOfTeams):
    
    numberOfRounds = 2*(numberOfTeams-1)
    # The solution will be a 2-dimensional array (a.k.a. the schedule)
    solution = np.zeros((numberOfTeams,numberOfRounds), dtype=int)
    
    # Finds canonical pattern to creat a feasible single round robin schedule
    games = findCanonicalPattern(numberOfTeams, numberOfRounds)
    
    # Creates first half of the tournament
    for i in range(numberOfRounds//2):
        
        for k in range(numberOfTeams//2):
            
            # Every edge of the canonical pattern is a game between the two nodes
            edge = games[i][k]
            
            teamA = int(edge[0])
            teamB = int(edge[1])
            
            # One team plays at home, one team plays away
            solution[teamA - 1][i] = teamB
            solution[teamB - 1][i] = - teamA
    
    # To create second half, mirror the first half inverting the signs
    temp = solution.copy()
    temp = -1*np.roll(temp, numberOfRounds//2, axis=1)
    solution = solution+temp

    return(solution)

def writeSchedule(S, filename):
    with open(filename,'w') as f:
        for x in S:
            for y in x:
                f.write(f"{y} ")
            f.write("\n")

def generate_schedule():
    schedule = getInitialSolution(count_teams())
    writeSchedule(schedule,"input/s0.txt")

def count_teams():
    with open("input/teams.txt",'r') as f:
        return len(f.readlines())

def get_costs(numberOfWorkers):
    costs = []
    for i in range(numberOfWorkers):
        with open(f"output/costs/cost_{i}.txt","r") as f:
            costs.append(float(f.read().strip()))

    return costs 

def sort_costs(costs):
    enumrated_cost = []
    for i in range(len(costs)):
        enumrated_cost.append((i,costs[i]))
    return dict(sorted(enumrated_cost, key=lambda x:x[1]))

def copy(dest,src):
    f1 = open(dest,"w")
    f2 = open(src,"r")
    data = f2.read()
    f1.write(data)
    f1.close()
    f2.close()

def update_schedule(numberOfWorkers):
    cost_dict = sort_costs(get_costs(numberOfWorkers))
    for i in range(3):
        copy(f"input/s{i}.txt",f"output/schedules/schedule_{list(cost_dict.keys())[0]}.txt")

def process_user_input(data):
    data = json.loads(data)
    locs = []
    with open("input/teams.txt","w") as f:
        for team in data:
            f.write(f"{team['name']}:{team['abbr']}\n")
            locs.append(tuple([float(x) for x in team["location"].split(',')]))
    with open("input/distances.txt","w") as f:
        for i in range(len(locs)):
            for j in range(len(locs)):
                if i==j:
                    f.write("0 ")
                else:
                    f.write(f"{distance_calculator(locs[i],locs[j])} ")
            f.write("\n")


def distance_calculator(loc1,loc2):
    R = 6371
    p1 = loc1[0]*np.pi/180
    p2 = loc2[0]*np.pi/180
    dp = (loc2[0]-loc1[0])*np.pi/180
    dl = (loc2[1]-loc1[0])*np.pi/180
    a = np.sin(dp/2)**2 + np.cos(p1)*np.cos(p2) + np.sin(dl/2)**2
    c = 2*np.arctan2(np.sqrt(a),np.sqrt(1-a))
    return c; #distance without scaling to radius of earth     
