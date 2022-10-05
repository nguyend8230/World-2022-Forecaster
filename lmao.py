f = open("MSI_results.csv")
lines = f.readlines()


msi_elo_dict = { "" : 0 }
k = 1000
for line in lines:
    chunks = line.split(",")
    if chunks[0] not in msi_elo_dict:
        msi_elo_dict[chunks[0]] = 1000
    if chunks[1] not in msi_elo_dict:
        msi_elo_dict[chunks[1]] = 1000
    p1 = (1.0 / (1.0 + pow(10, ((msi_elo_dict[chunks[1]] - msi_elo_dict[chunks[0]]) / 400))))
    p2 = (1.0 / (1.0 + pow(10, ((msi_elo_dict[chunks[0]] - msi_elo_dict[chunks[1]]) / 400))))
    old_elo_1 = msi_elo_dict[chunks[0]]
    old_elo_2 = msi_elo_dict[chunks[1]]
    msi_elo_dict[chunks[0]] = msi_elo_dict[chunks[0]] + k*((chunks[2] == "Victory") - p1)
    msi_elo_dict[chunks[1]] = msi_elo_dict[chunks[1]] + k*((chunks[2] == "Defeat") - p2)

msi_elo_dict = sorted(msi_elo_dict.items(), key=lambda item: item[1])
f.close()

#---------------------------------------------------------------------------------------------

f = open("region.csv")
lines = f.readlines()

regions_dict = { "" : ""}
for line in lines:
    chunks = line.split(",")
    regions_dict[chunks[0]] = chunks[1] 

f.close()

#---------------------------------------------------------------------------------------------

elo_multiplier_dict = { "" : 0 }
for elo in msi_elo_dict:
    if elo[0] in regions_dict:
        elo_multiplier_dict[regions_dict[elo[0]]] = elo[1]/1000

#---------------------------------------------------------------------------------------------
f = open("results.csv")
lines = f.readlines()

world_elo_dict = { "" : 0 }
k = 1000
for line in lines:
    chunks = line.split(",")
    if chunks[0] not in world_elo_dict:
        world_elo_dict[chunks[0]] = 1000
    if chunks[1] not in world_elo_dict:
        world_elo_dict[chunks[1]] = 1000
    p1 = (1.0 / (1.0 + pow(10, ((world_elo_dict[chunks[1]] - world_elo_dict[chunks[0]]) / 400))))
    p2 = (1.0 / (1.0 + pow(10, ((world_elo_dict[chunks[0]] - world_elo_dict[chunks[1]]) / 400))))
    old_elo_1 = world_elo_dict[chunks[0]]
    old_elo_2 = world_elo_dict[chunks[1]]
    world_elo_dict[chunks[0]] = world_elo_dict[chunks[0]] + k*((chunks[2] == "Victory") - p1)
    world_elo_dict[chunks[1]] = world_elo_dict[chunks[1]] + k*((chunks[2] == "Defeat") - p2)

# print(world_elo_dict)
f.close()

#---------------------------------------------------------------------------------------------
f = open("world teams.csv")
lines = f.readlines()

result = { "" : 0 }

for line in lines:
    chunks = line.split(",")
    if chunks[0] in world_elo_dict:
        # print(world_elo_dict[chunks[0]])
        result[chunks[0]] = world_elo_dict[chunks[0]] * elo_multiplier_dict[chunks[1]]
    else:
        print(chunks[0])


result = sorted(result.items(), key=lambda item: item[1])
print(result)
