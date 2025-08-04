import random
import discord
from player import Player
from discord.ext import commands
import discord_commands

async def perform_night_actions(idtoplayers, roletoplayers, Roles, Members,ctx):
        FORBIDDEN = {"table1", "table2", "table3"}
        rolenumber = 0
        Cycle = ["Werewolf","Minion","Mason","Seer","Robber","Troublemaker","Insomniac"]
        for role in Cycle:
            if role in Roles:
                if rolenumber == 0:
                    obj = roletoplayers["Werewolf"]
                    obj2 = roletoplayers["Werewolf2"]
                    name1 = obj.ID()
                    name2 = obj2.ID()
                    if name1 not in FORBIDDEN and name2 not in FORBIDDEN:
                        await discord_commands.send_dm(ctx, name1,name1 + " and " + name2 + " are Werewolves")
                        await discord_commands.send_dm(ctx, name2,name1 + " and " + name2 + " are Werewolves")
                    else:
                        await discord_commands.send_dm(ctx, name1,"There are only one of you")
                        await discord_commands.send_dm(ctx, name2,"There are only one of you")
                elif rolenumber == 1:
                    obj = roletoplayers["Minion"]
                    print(obj.Role())
                elif rolenumber == 2:
                    obj = roletoplayers["Mason"]
                    obj2 = roletoplayers["Mason2"]
                    name1 = obj.ID()
                    name2 = obj2.ID()
                    if name1 not in FORBIDDEN and name2 not in FORBIDDEN:
                        await discord_commands.send_dm(ctx, name1,name1 + " and " + name2 + " are Masons")
                        await discord_commands.send_dm(ctx, name2,name1 + " and " + name2 + " are Masons")
                    else:
                        await discord_commands.send_dm(ctx, name1,"There are only one of you")
                        await discord_commands.send_dm(ctx, name2,"There are only one of you")

                elif rolenumber == 3:
                    obj = roletoplayers["Seer"]
                    print(obj.Role())
                elif rolenumber == 4:
                    obj = roletoplayers["Robber"]
                    print(obj.Role())
                elif rolenumber == 5:
                    obj = roletoplayers["Troublemaker"]
                    print(obj.Role())
                elif rolenumber == 6:
                    obj = roletoplayers["Insomniac"]
                    print(obj.Role())
                rolenumber += 1
            else:
                rolenumber += 1

async def make_onuw(playerIDs, members, playerNames , ctx):
    playern = len(members)
    print("player count")
    print(playern)
    Roleskeep = []
    players = []
    for x in playerIDs:
        players.append(x.name)
    players.append("table1")
    players.append("table2")
    players.append("table3")

    print(len(players))

    if playern == 3:
        Roles = ["Villager","Robber","Troublemaker", "Seer"]
    elif playern == 4:
        Roles = ["Robber","Troublemaker", "Mason", "Mason2", "Seer"]
    elif playern > 4:
        Roles = ["Robber","Troublemaker", "Mason", "Mason2", "Insomniac", "Tanner", "Villager", "Seer"]
    else:
        print("Not Enough")
        Roles = ["Robber","Troublemaker", "Mason", "Mason2", "Insomniac", "Tanner", "Villager", "Seer"]

    playerIDtoOBJ = {}
    RolestoOBJ = {}
    m2 = False

    DRoles = Roles

    
    random.seed()
    random.shuffle(players)
    random.shuffle(players)
    random.shuffle(players)
    n=0
    y=0
    role = "Werewolf"
    x = players[0]
    print(x,role)
    obj = Player(x,role)
    playerIDtoOBJ[obj.ID()] = obj
    RolestoOBJ[obj.Role()] = obj
    Roleskeep.append(role)
    playern -= 1
    role = "Werewolf2"
    x = players[1]
    print(x,role)
    obj = Player(x,role)
    playerIDtoOBJ[obj.ID()] = obj
    RolestoOBJ[obj.Role()] = obj
    Roleskeep.append(role)
    playern -= 1
    for x in players[2:]:
        print(x)
        role = DRoles[y]
        print(x,role)
        obj = Player(x,role)
        playerIDtoOBJ[obj.ID()] = obj
        RolestoOBJ[obj.Role()] = obj
        Roleskeep.append(DRoles[y])
        DRoles.remove(DRoles[y])
        playern -= 1

    print(Roles)
    print(DRoles)
    print(Roleskeep)

    print(playerIDtoOBJ)

    for i in range(len(players)):
        obj = playerIDtoOBJ[players[i]]
        print(obj)
        await discord_commands.send_dm(ctx, obj.ID(),"The Epic Game Has Started!")
        await discord_commands.send_dm(ctx, obj.ID(),"You are the " + obj.Role())
        await discord_commands.send_dm(ctx, obj.ID(),"The Night phase is starting...")

    await perform_night_actions(playerIDtoOBJ, RolestoOBJ, Roleskeep, members, ctx)