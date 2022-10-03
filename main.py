# have a map for each team
# initial elo for each team is 1000
# if the elo of the team == 0
#     set elo to 1000 then do calculation
f = open("LCS.csv")
lines = f.readlines()

elo_dict = { "" : 0 }
team_list = []
k = 400
for line in lines:
    chunks = line.split(",")
    if chunks[0] not in elo_dict:
        elo_dict[chunks[0]] = 1000
        team_list.append(chunks[0])
    if chunks[1] not in elo_dict:
        elo_dict[chunks[1]] = 1000
        team_list.append(chunks[1])
    p1 = (1.0 / (1.0 + pow(10, ((elo_dict[chunks[1]] - elo_dict[chunks[0]]) / 400))))
    p2 = (1.0 / (1.0 + pow(10, ((elo_dict[chunks[0]] - elo_dict[chunks[1]]) / 400))))
    old_elo_1 = elo_dict[chunks[0]]
    old_elo_2 = elo_dict[chunks[1]]
    elo_dict[chunks[0]] = elo_dict[chunks[0]] + k*((chunks[2] == "Victory") - p1)
    elo_dict[chunks[1]] = elo_dict[chunks[1]] + k*((chunks[2] == "Defeat") - p2)

test = sorted(elo_dict.items(), key=lambda item: item[1])

print(test)
    