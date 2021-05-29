import argparse 
import numpy as np 
import random
import math
from numpy.testing._private.utils import requires_memory 

def getDistances(filename: str):
    dist = []
    with open(filename) as f:
        for line in f:
            dist.append([float(x) for x in line.split()])
    return dist 

def getSchedule(filename: str):
    s = []
    with open(filename,'r') as f:
        data = f.read()
        lines = data.split('\n')
        for l in lines:
            s.append([int(x) for x in l.split()])
    return np.array(s[:-1])

def writeSchedule(S, filename):
    with open(filename,'w') as f:
        for x in S:
            for y in x:
                f.write(f"{y} ")
            f.write("\n")

def SA(S,dist,T,maxP,maxC,maxR,beta,weight,teta):
    numberOfTeams, numberOfRounds = S.shape
    print(S.shape)
    numberOfViolations = 0

    def swapHomes(S):
        newS = np.copy(S)
        teamA = random.randint(0,numberOfTeams-1)
        teamB = random.randint(0,numberOfTeams-1)
        for i in range(numberOfRounds):
            if abs(S[teamA][i]) == teamB + 1:
                newS[teamA][i] = -S[teamA][i]
                newS[teamB][i] = -S[teamB][i]

        return newS

    def swapRounds(S):
        newS = np.copy(S)
        roundAindex = random.randint(0,numberOfRounds - 1)  
        roundBindex = random.randint(0,numberOfRounds - 1)          
        newS[:,[roundAindex,roundBindex]] =  newS[:,[roundBindex,roundAindex]]
        return newS

    def swapTeams(S):
        newS = np.copy(S)
        teamA = random.randint(0,numberOfTeams-1)
        teamB = random.randint(0,numberOfTeams-1)

        for i in range(numberOfRounds):
            if abs(S[teamA][i]) != teamB+1:
                newS[[teamA,teamB],i] = newS[[teamB,teamA],i]

                formerAdversaryTeamA = abs(S[teamA][i]) - 1
                formerAdversaryTeamB = abs(S[teamB][i]) - 1

                if S[formerAdversaryTeamA][i] > 0:
                    newS[formerAdversaryTeamA][i] = teamB + 1
                else:
                    newS[formerAdversaryTeamA][i] = -(teamB + 1)
                
                if S[formerAdversaryTeamB][i] > 0:
                    newS[formerAdversaryTeamB][i] = teamA + 1
                else:
                    newS[formerAdversaryTeamB][i] = -(teamA+1)

        return newS 

    #todo: implement partialSwapRounds

    def partialSwapTeams(S):
        newS = np.copy(S)
    
        round = random.randint(0,numberOfRounds - 1)
        teamA = random.randint(0,numberOfTeams - 1)
        teamB = random.randint(0,numberOfTeams - 1)
                    
        adversaryA = S[teamA][round]
        adversaryB = S[teamB][round]
                    
        if abs(adversaryB) != teamA + 1:                
            newS[[teamA,teamB],round] =  newS[[teamB,teamA],round]            
            affectedTeamA = abs(adversaryA)
            affectedTeamB = abs(adversaryB)
                            
            oppositeA = S[affectedTeamA - 1][round]
            oppositeB = S[affectedTeamB - 1][round]
                        
            if oppositeA > 0:                    
                newS[affectedTeamA - 1][round] = abs(oppositeB)
            else:                    
                newS[affectedTeamA - 1][round] = - abs(oppositeB)
            
            if oppositeB > 0:                    
                newS[affectedTeamB - 1][round] = abs(oppositeA)
            else:                    
                newS[affectedTeamB - 1][round] = - abs(oppositeA)        
                        
            currentAdversaryB = adversaryB
                        
            while currentAdversaryB != adversaryA:
        
                currentAdversaryA = currentAdversaryB
                            
                i = np.nonzero(S[teamA] == currentAdversaryA)[0][0]
                                    
                currentAdversaryB = S[teamB][i]
                            
                newS[[teamA,teamB],i] =  newS[[teamB,teamA],i]
                        
                affectedTeamA = abs(currentAdversaryA)
                affectedTeamB = abs(currentAdversaryB)
                            
                oppositeA = S[affectedTeamA - 1][i]
                oppositeB = S[affectedTeamB - 1][i]
                            
                if oppositeA > 0:                 
                    newS[affectedTeamA - 1][i] = abs(oppositeB)
                else:
                    newS[affectedTeamA - 1][i] = - abs(oppositeB)

                if oppositeB > 0:                
                    newS[affectedTeamB - 1][i] = abs(oppositeA)
                else:                
                    newS[affectedTeamB - 1][i] = - abs(oppositeA)
        return newS

    for i in range(numberOfTeams):
        count = 0
        for k in range(1,numberOfRounds):
            if (S[i][k]>0 and S[i][k-1]>0) or (S[i][k]<0 and S[i][k-1]<0):
                count += 1
            else:
                count = 0
            
            if count > 2:
                numberOfViolations  += 1
            
            if abs(S[i][k]) == abs(S[i][k-1]):
                numberOfViolations += 1

    violationsS = numberOfViolations
    totaldistance = 0 

    distanceS = np.copy(S)
    for x in range(numberOfTeams):
        distanceS[x] = [x+1 if i>0 else abs(i) for i in distanceS[x]]
        totaldistance += dist[distanceS[x][-1]-1][x]
    costS = totaldistance

    if violationsS != 0:
        costS = math.sqrt((costS**2)+(weight*(1+math.sqrt(violationsS)*math.log(violationsS/float(2))))**2)

    bestFeasible = 9999999
    nbf = 9999999

    bestInfeasible = 9999999
    nbi = 9999999

    reheat = 0
    counter = 0

    while reheat <= maxR:
        phase = 0
        while phase<=maxP:
            counter = 0
            while counter <= maxC:
                chooseMove = random.randint(0,3)

                if chooseMove == 0:
                    newS = swapHomes(S)
                elif chooseMove == 1:
                    newS = swapRounds(S)
                elif chooseMove == 2:
                    newS = swapTeams(S)
                #elif chooseMove == 3:
                #    newS = partialSwapRounds(S)
                elif chooseMove == 3:
                    newS = partialSwapTeams(S)
                #print(newS)
                numberOfViolations = 0
                for i in range(numberOfTeams):
                    count = 0
                    for k in range(1,numberOfRounds):
                        if (newS[i][k] > 0 and newS[i][k-1] > 0) or (newS[i][k] < 0 and newS[i][k-1] < 0):
                            count += 1
                        else:
                            count = 0

                        if count > 2:
                            numberOfViolations += 1
                        
                        if abs(newS[i][k]) == abs(newS[i][k-1]):
                            numberOfViolations += 1 

                violationsNewS = numberOfViolations
                
                totaldistance = 0
                distanceNewS = np.copy(newS)
                
                for x in range(numberOfTeams):
                    distanceNewS[x] = [x + 1 if i > 0 else abs(i) for i in distanceNewS[x]]    
                    totaldistance += dist[x][distanceNewS[x][0]-1]    
                    for y in range(numberOfRounds - 1):        
                        totaldistance += dist[distanceNewS[x][y]-1][distanceNewS[x][y + 1]-1]        
                    totaldistance += dist[distanceNewS[x][-1] - 1][x]

                costNewS = totaldistance
                
                if violationsNewS != 0:                
                    costNewS = math.sqrt((costNewS**2) + (weight*(1 + math.sqrt(violationsNewS)*math.log(violationsNewS/float(2))))**2)
                
                if costNewS < costS or (violationsNewS == 0 and costNewS < bestFeasible) or (violationsNewS > 0 and costNewS < bestInfeasible):                    
                    accept = 1
                else:
                    delta = float(costNewS-costS)
                    probability = math.exp(-(delta/T))
                    chance = random.random()
                    if chance < probability:
                        accept = 1
                    else:
                        accept = 0
                
                if accept == 1:
                    S = newS                    
                    violationsS = violationsNewS                    
                    costS = costNewS                    
                    if violationsS == 0:                        
                        nbf = min(costS, bestFeasible)                    
                    else:                
                        nbi = min(costS, bestInfeasible)
                    
                    if nbf < bestFeasible or nbi < bestInfeasible:                        

                        reheat = 0
                        counter = 0
                        phase = 0
                        
                        bestTemperature = T
                        
                        bestFeasible = nbf
                        bestInfeasible = nbi
                        
                        if violationsS == 0:                            
                            weight = weight/teta
                        else:
                            weight = weight*teta
                              
                else:                        
                    counter += 1
                
            phase += 1
            T = T*beta
                            
        reheat += 1   
        T = 2*bestTemperature

    return S, costS

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--process',type=int,required=True)
    parser.add_argument('--temp',type=float,default=400)
    parser.add_argument('-p',type=int,default=12)
    parser.add_argument('-c',type=int,default=10)
    parser.add_argument('-r',type=int,default=2)
    parser.add_argument('-b',type=float,default=0.999)
    parser.add_argument('-w',type=float,default=4000)
    parser.add_argument('--teta',type=float,default=1.04)   
    args = parser.parse_args()

    S = getSchedule("schedule.txt")
    dist = getDistances("distances.txt")
    S, costS = SA(S,dist,args.temp,args.p,args.c,args.r,args.b,args.w,args.teta)
    writeSchedule(S,f"schedule_{args.process}.txt")
    with open(f"cost_{args.process}.txt","w") as f:
        f.write(str(costS))
