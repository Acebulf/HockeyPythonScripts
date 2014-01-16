import gspread
import time
from decimal import Decimal

user = raw_input("Username:")
password = raw_input("Password:")

starttime = time.time()

print "\nLogging in"
gc = gspread.login(user, password)

worksheet = gc.open_by_key("0AmFkEwg9IezIdHNiMWM4N01icVl3a2lFNkNNS2NCNFE").get_worksheet(0)


f = open("output.txt", "w")
print "Logged in, fetching team stats"


class Team:
    def __init__(self, row, col, name):
        self.name = name
        self.GP = int(worksheet.cell(row, col).value)
        self.wins = int(worksheet.cell(row+1, col).value)
        self.losses = int(worksheet.cell(row+2, col).value)
        self.OT = int(worksheet.cell(row+3, col).value)
        self.streak = worksheet.cell(row+5, col).value

        self.points = 2*self.wins + self.OT

        self.goals_for = int(worksheet.cell(row, col+5).value)
        self.assists = int(worksheet.cell(row+1, col+5).value)
        self.goals_against = int(worksheet.cell(row+2, col+5).value)
        self.saves = int(worksheet.cell(row+3, col+5).value)
        self.shutout = int(worksheet.cell(row+5, col+5).value)

        if self.saves == 0:
            self.save_percentage = Decimal(0)
        else:
            self.save_percentage = Decimal(self.saves)/(Decimal(self.saves + self.goals_against))

        if self.GP == 0:
            self.goals_for_per_game = 0
            self.assists_per_game = 0
            self.goals_against_per_game = 0
            self.saves_per_game = 0
            self.goal_differential = 0
            self.win_percentage = 0
        else:
            self.goals_for_per_game = Decimal(self.goals_for) / Decimal(self.GP)
            self.assists_per_game = Decimal(self.assists)/Decimal(self.GP)
            self.goals_against_per_game = Decimal(self.goals_against) / Decimal(self.GP)
            self.saves_per_game = Decimal(self.saves) / Decimal(self.GP)
            self.goal_differential = self.goals_for - self.goals_against
            self.win_percentage = Decimal(self.wins) / Decimal(self.GP)

        self.record = "{0}-{1}-{2}".format(self.wins, self.losses, self.OT)

    def print_standings(self):
        return "|{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}%|".format("{0}", self.name, self.record, self.points, self.streak,
                                                           self.goals_for, self.goals_against,
                                                          (self.save_percentage*100).quantize(Decimal(".01")))

standings = [Team(3, 2, "BOS"), Team(23, 2, "DET"), Team(3, 18, "CHI"), Team(23, 18, "NJD"), Team(3, 34, "COL"),
             Team(23, 34, "WSH")]


ranked_teams = sorted(standings, key=lambda team: (team.points, team.wins), reverse=True)

f.write("|Rank|Team|Record|Pts|Streak|GF|GA|Sv %|\n")
f.write("|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n")

for x in ranked_teams:
    f.write(x.print_standings().format(ranked_teams.index(x) + 1) + "\n")

f.write("\n\n")
print "Fetching player stats"
class Player:
    def __init__(self, row, col, team=None):
        if worksheet.cell(row, col).value in (None, "None", ""):
            self.kill = True

        elif col not in (1, 17, 33):
            raise ValueError

        else:
            self.kill = False

            self.team = team

            self.name = worksheet.cell(row, col).value
            self.pos = worksheet.cell(row, col + 1).value
            self.role = worksheet.cell(row, col + 2).value
            # skip points to reduce requests
            self.goals = int(worksheet.cell(row, col + 4).value)
            self.assists = int(worksheet.cell(row, col + 5).value)
            # skip ppg

            #lol canadave doesn't have a plus/minus lelelelel
            self.plus_minus = worksheet.cell(row, col + 7).value

            if self.plus_minus == None:
                self.plus_minus = 0
            else:
                self.plus_minus = int(self.plus_minus)

            self.gwg = int(worksheet.cell(row, col+8).value)
            self.games_played = int(worksheet.cell(row, col + 13).value)

            # goalie bullshit
            self.saves = int(worksheet.cell(row, col + 9).value)
            self.goals_against = int(worksheet.cell(row, col + 11).value)
            self.games_played_goalie = int(worksheet.cell(row, col + 14).value)

            #automade stats
            self.points = self.goals+self.assists

            if self.games_played == 0:
                self.ppg = 0
            else:
                self.ppg = Decimal(self.points)/Decimal(self.games_played)

            if self.saves == 0:
                self.save_percentage = Decimal(0)
            else:
                self.save_percentage = Decimal(self.saves)/(Decimal(self.saves + self.goals_against))

            if self.games_played_goalie == 0:
                self.gaa = 100.0        # or other arbitrarily large number
            else:
                self.gaa = Decimal(self.goals_against) / Decimal(self.games_played_goalie)

    def print_top10_forward(self):
        return "|{9}|{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}|".format(self.name, self.team, self.pos[0], self.points,
                                                                  self.goals, self.assists, (self.ppg).quantize(Decimal(".01")),
                                                                  self.plus_minus, self.games_played, "{0}")

    def print_top3_goalie(self):
        return "|{0}|{1}|{2}|{3}|{4}%|{5}|{6}|{7}|".format("{0}", self.name, self.team, self.saves,
                                                          (self.save_percentage*100).quantize((Decimal(".01"))),
                                                            self.goals_against, self.gaa.quantize(Decimal(".01")), self.games_played_goalie)
playerlist = []

top_rows = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
bottom_rows = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
first_col = 1
second_col = 17
third_col = 33


def assignList(row_list, start_column, team_name):
    for x in row_list:
        player = Player(x, start_column, team_name)
        if player.kill == False:
            playerlist.append(player)

    print "--> "+ team_name + " players assigned"

assignList(top_rows, first_col, "BOS")
assignList(top_rows, second_col, "CHI")
assignList(top_rows, third_col, "COL")
assignList(bottom_rows, first_col, "DET")
assignList(bottom_rows, second_col, "NJD")
assignList(bottom_rows, third_col, "WSH")

print "Player stats fetched, building top 10 forwards"

top10 = sorted(playerlist, key=lambda player: (player.points, player.ppg), reverse=True)[:10]

for x in top10:
    f.write(x.print_top10_forward().format(top10.index(x)+1)+"\n")

f.write("\n\n")
print "Top 10 forwards list built and logged to file"
print "Building Top 3 goaltenders list"

def sortkey(player):
    """
    Returns the save percentage as 0 if player has not played 50%
    of his team's games as goalie
    """

    for team in standings:
        if team.name == player.team:
            if Decimal(player.games_played_goalie) < 10:
                savep = 0
            else:
                savep = player.save_percentage

    return (-savep, player.gaa)

top3 = sorted(playerlist, key=lambda player: sortkey(player))[:3]

for x in top3:
    f.write((x.print_top3_goalie() + "\n").format(top3.index(x) + 1))

f.close()
print "Done"
print "Runtime: {0}".format(time.time()-starttime)