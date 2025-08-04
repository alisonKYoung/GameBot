import random
import discord
from player import Player
from discord.ext import commands
import discord_commands

def perform_night_actions(idtoplayers, roletoplayers, Roles):
        rolenumber = 0
        #obj = roletoplayers["Villager"]
        #print(obj.Role())
        #obj = roletoplayers["Hunter"]
        #print(obj.Role())
        #obj = roletoplayers["Tanner"]
        #print(obj.Role())
        Cycle = ["Werewolf","Minion","Mason","Seer","Robber","Troublemaker","Drunk","Insomniac","Villager","Hunter"]
        for role in Cycle:
            if role not in Roles:
                if rolenumber == 0:
                    obj = roletoplayers["Doppelganger"]
                    print(obj.Role())
                elif rolenumber == 1:
                    if "Werewolf2" not in Roles:
                        obj = roletoplayers["Werewolf"]
                        obj2 = roletoplayers["Werewolf2"]
                        print(obj.Role() + " and " + obj2.Role()) 
                    else:
                        obj = roletoplayers["Werewolf"]
                        print(obj.Role())
                elif rolenumber == 2:
                    obj = roletoplayers["Minion"]
                    print(obj.Role())
                elif rolenumber == 3:
                    obj = roletoplayers["Mason"]
                    obj2 = roletoplayers["Mason2"]
                    print(obj.ID() + " and " + obj2.ID())
                elif rolenumber == 4:
                    obj = roletoplayers["Seer"]
                    print(obj.Role())
                elif rolenumber == 5:
                    obj = roletoplayers["Robber"]
                    print(obj.Role())
                elif rolenumber == 6:
                    obj = roletoplayers["Troublemaker"]
                    print(obj.Role())
                elif rolenumber == 7:
                    obj = roletoplayers["Drunk"]
                    print(obj.Role())
                elif rolenumber == 8:
                    obj = roletoplayers["Insomniac"]
                    print(obj.Role())
                rolenumber += 1
            else:
                rolenumber += 1

async def make_onuw(playerIDs, members, playerNames):
    playern = len(members)
    print("player count")
    print(playern)
    Roleskeep = ["Doppelganger","Werewolf","Werewolf2","Minion","Mason","Seer","Robber","Troublemaker","Drunk","Insomniac","Villager","Hunter","Tanner"]
    Roles = ["Doppelganger","Werewolf","Werewolf2","Minion","Mason","Seer","Robber","Troublemaker","Drunk","Insomniac","Villager","Hunter","Tanner"]
    playerIDtoOBJ = {}
    RolestoOBJ = {}
    m2 = False

    random.seed()

    random.shuffle(Roles)

    y=0
    for x in playerIDs:
        if playern == 1 and Roles[y] == "Mason":
            y = 1
        else:
            role = Roles[y]
            if m2:
                role = "Mason2"
            print(x,role)
            obj = Player(x,role)
            playerIDtoOBJ[obj.ID()] = obj
            RolestoOBJ[obj.Role()] = obj
            if m2 != True:
                Roles.remove(Roles[y])
            else:
                m2 = False
            if role == ("Mason"):
                m2 = True
            playern -= 1

    print(Roles)

    print(playerIDtoOBJ)

    for i in range(len(playerNames)):
        obj = playerIDtoOBJ[playerNames[i]]
        await discord_commands.send_dm(members[i],"The Game Has Started!")
        await discord_commands.send_dm(members[i],"You are the " + obj.Role())
        await discord_commands.send_dm(members[i],"The Night phase is starting...")

    #perform_night_actions(playerIDtoOBJ, RolestoOBJ, Roles)