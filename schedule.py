#Schedule-generator for LHL use written by Acebulf (acebulf at gmail.com)
#Current version 1.0 -- Jan 16 2014
#Copyrighted under the MIT License (see License included in the github repo)

import random
import time

while 1:
    print "Starting random-schedule generation process..."
    starttime = time.time()
    kill = False
    schedule = [[]]*30

    teams = ["BOS", "CHI", "COL", "DET", "NJD", "WSH"]
    # Randomly Choose Team
    team1 = random.choice(teams)
    teams_mt1 = list(teams)
    teams_mt1.remove(team1)

    matchups = []

    for x in teams_mt1:
        for y in xrange(6):
            matchups.append((team1,x))
    random.shuffle(matchups)

    for x in xrange(30):
        schedule[x]=[matchups[x]]

    team2 = random.choice(teams_mt1)
    teams_2 = list(teams_mt1)
    teams_2.remove(team2)
    matchups=[]
    for x in teams_2:
        for y in xrange(6):
            matchups.append((team2,x))
    random.shuffle(matchups)

    days = range(30)

    def playing_day(team, day):
        occupied = [i[0] for i in day] + [i[1] for i in day]
        return (team in occupied)

    for matchup in matchups:
        while 1:
            temp_day = random.choice(days)
            if time.time()-starttime >= 4:
                kill = True
                break
            if not playing_day(matchup[0],schedule[temp_day]) and not playing_day(matchup[1],schedule[temp_day]):
                schedule[temp_day].append(matchup)
                days.remove(temp_day)
                break
    if kill:
        print "Error in stage 1; restarting"
        continue

    print "Stage 1/3 Successfully Completed!"
    days2games = list(schedule)
    days1game = []
    try:
        for x in xrange(30):
            if len(days2games[x]) == 1:
                days1game.append(days2games.pop(x))
    except IndexError:
        pass

    team3 = random.choice(teams_2)
    teams_3 = list(teams_2)
    teams_3.remove(team3)

    matchups=[]

    for x in teams_3:
        matchups.append((team3,x))

    team4 = random.choice(teams_3)
    teams_4 = list(teams_3)
    teams_4.remove(team4)

    for x in teams_4:
        matchups.append((team4,x))

    matchups.append((teams_4[0],teams_4[1]))
    for x in days2games:
        for y in matchups:
            if not playing_day(y[0],x) and not playing_day(y[1],x):
                x.append(y)

    newmatchups = []
    for x in matchups:
        newmatchups.append(x)
        newmatchups.append(x)

    random.shuffle(newmatchups)

    print "Stage 2/3 Successfully Completed!"
    for x in days1game:
        for y in newmatchups:
            if not playing_day(y[0],x) and not playing_day(y[1],x):
                x.append(y)
                newmatchups.remove(y)

    for x in schedule:
        if len(x) != 3:
            print "Problem encountered in stage 3; Restarting..."
            kill=True
            break
    if kill:
        continue
    print "Stage 3/3 Successfully Completed"
    break

print "Schedule Successfully Generated"
print "Printing to File..."

f = open("schedule.txt","w")

dayno = 0
while dayno <= 29:
    f.write("Day {0}:\n".format(dayno+1))
    for x in schedule[dayno]:
        f.write(x[0] + " - " + x[1]+"\n")

    f.write("\n")
    dayno += 1

print "Result written to file. Program terminating."
