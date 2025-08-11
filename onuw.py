import random
import discord
from player import Player
from discord.ext import commands
import discord_commands
from collections import Counter

async def perform_night_actions(idtoplayers, roletoplayers, Roles, Members, ctx):
        FORBIDDEN = {"table1", "table2", "table3"}
        rolenumber = 0
        Cycle = ["Werewolf","Minion","Mason","Seer","Robber","Troublemaker","Insomniac","Mason2","Werewolf2"]
        for role in Cycle:
            if role in Roles:
                if rolenumber == 0:
                    obj = roletoplayers["Werewolf"]
                    obj2 = roletoplayers["Werewolf2"]
                    name1 = obj.ID()
                    name2 = obj2.ID()
                    if name1 not in FORBIDDEN or name2 not in FORBIDDEN:
                        if name1 not in FORBIDDEN and name2 not in FORBIDDEN:
                            # Both are humans → tell them about each other
                            await discord_commands.send_dm(ctx, name1, f"{name1} and {name2} are Werewolves")
                            await discord_commands.send_dm(ctx, name2, f"{name1} and {name2} are Werewolves")
                        else:
                            # Find the human Werewolf
                            if name1 not in FORBIDDEN:
                                human = name1
                            else:
                                human = name2

                            # Ask the human to pick a middle card
                            choice = await discord_commands.send_dm_with_reactions(
                                ctx.bot, ctx, human,
                                "There is only one Werewolf. Pick a middle card:",
                                ["1️⃣", "2️⃣", "3️⃣"]
                            )

                            # Map choice to table card
                            if choice == "1️⃣":
                                table = idtoplayers["table1"]
                            elif choice == "2️⃣":
                                table = idtoplayers["table2"]
                            elif choice == "3️⃣":
                                table = idtoplayers["table3"]

                            tablename = table.Role()

                            # Send the results to both werewolf slots (human & table)
                            await discord_commands.send_dm(ctx, human, f"The role in center {choice} is {tablename}")

                            other = name1 if human == name2 else name2
                            if other not in FORBIDDEN:
                                await discord_commands.send_dm(ctx, other, f"The role in center {choice} is {tablename}")

                            print(f"{human} picked middle card {choice} → {tablename}")                      
                elif rolenumber == 1:  # Minion
                    obj = roletoplayers["Minion"]
                    minion_name = obj.ID()

                    # Find all human Werewolves (not in FORBIDDEN)
                    werewolves = []
                    for role_key in ["Werewolf", "Werewolf2"]:
                        if role_key in roletoplayers:
                            w_obj = roletoplayers[role_key]
                            w_name = w_obj.ID()
                            if w_name not in FORBIDDEN:
                                werewolves.append(w_name)

                    if werewolves:
                        werewolf_list = ", ".join(werewolves)
                        await discord_commands.send_dm(ctx, minion_name, f"You are the Minion. The Werewolves are: {werewolf_list}.")
                    else:
                        await discord_commands.send_dm(ctx, minion_name, "You are the Minion. There are no human Werewolves.")
                elif rolenumber == 2:
                    obj = roletoplayers["Mason"]
                    obj2 = roletoplayers["Mason2"]
                    name1 = obj.ID()
                    name2 = obj2.ID()
                    if name1 in FORBIDDEN and name2 in FORBIDDEN:
                        return
                    else:
                        if name1 not in FORBIDDEN and name2 not in FORBIDDEN:
                            await discord_commands.send_dm(ctx, name1,name1 + " and " + name2 + " are Masons")
                            await discord_commands.send_dm(ctx, name2,name1 + " and " + name2 + " are Masons")
                        else:
                            await discord_commands.send_dm(ctx, name1,"There are only one of you")
                            await discord_commands.send_dm(ctx, name2,"There are only one of you")
                elif rolenumber == 3:
                        obj = roletoplayers["Seer"]
                        seer_name = obj.ID()

                        # Ask the Seer what they want to do
                        choice = await discord_commands.send_dm_with_reactions(
                            ctx.bot, ctx, seer_name,
                            "You are the Seer. Do you want to:\n1️⃣ Look at another player's card\n2️⃣ Look at two cards from the center",
                            ["1️⃣", "2️⃣"]
                        )

                        if choice == "1️⃣":
                            # Show player options (excluding Seer & tables)
                            player_emojis = {}
                            emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
                            available_players = [p for p in idtoplayers.keys() if p not in FORBIDDEN and p != seer_name]
                            
                            for idx, player_id in enumerate(available_players):
                                player_emojis[emoji_list[idx]] = player_id
                            
                            # Ask which player to reveal
                            picked_player = await discord_commands.send_dm_with_reactions(
                                ctx.bot, ctx, seer_name,
                                "Pick a player to see their role:",
                                list(player_emojis.keys())
                            )

                            target_id = player_emojis[picked_player]
                            role_name = idtoplayers[target_id].Role()
                            await discord_commands.send_dm(ctx, seer_name, f"{target_id} is the {role_name}")

                        elif choice == "2️⃣":
                            # Ask for first center card
                            table_map = {"1️⃣": "table1", "2️⃣": "table2", "3️⃣": "table3"}
                            first_pick = await discord_commands.send_dm_with_reactions(
                                ctx.bot, ctx, seer_name,
                                "Pick your first center card:",
                                list(table_map.keys())
                            )
                            first_card = table_map[first_pick]
                            first_role = idtoplayers[first_card].Role()

                            # Ask for second center card (remove the first choice from options)
                            remaining_tables = {k: v for k, v in table_map.items() if v != first_card}
                            second_pick = await discord_commands.send_dm_with_reactions(
                                ctx.bot, ctx, seer_name,
                                "Pick your second center card:",
                                list(remaining_tables.keys())
                            )
                            second_card = remaining_tables[second_pick]
                            second_role = idtoplayers[second_card].Role()

                            await discord_commands.send_dm(ctx, seer_name,
                                f"Center card {first_card} is {first_role}, and {second_card} is {second_role}"
                            )
                elif rolenumber == 4:
                    obj = roletoplayers["Robber"]
                    robber_name = obj.ID()

                    # Build a map of other players to pick from (exclude robber)
                    valid_targets = [p for p in idtoplayers.keys() if p != robber_name and p not in {"table1", "table2", "table3"}]
                    emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]  # expand if needed
                    pick_map = {emoji_list[i]: valid_targets[i] for i in range(len(valid_targets))}

                    # Prompt robber to pick a player to swap with
                    choice = await discord_commands.send_dm_with_reactions(
                        ctx.bot, ctx, robber_name,
                        f"You are the Robber. Pick a player to swap roles with:\n" + 
                        "\n".join(f"{emoji} - {pick_map[emoji]}" for emoji in pick_map),
                        list(pick_map.keys())
                    )

                    target_id = pick_map[choice]

                    # Swap roles
                    robber_obj = idtoplayers[robber_name]
                    target_obj = idtoplayers[target_id]
                    robber_role_before = robber_obj.Role()
                    target_role_before = target_obj.Role()

                    robber_obj.ChangeRole(target_role_before)
                    target_obj.ChangeRole(robber_role_before)

                    await discord_commands.send_dm(ctx, robber_name, f"You swapped with {target_id}. Your new role is {robber_obj.Role()}.")

                elif rolenumber == 5:
                    obj = roletoplayers["Troublemaker"]
                    troublemaker_name = obj.ID()

                    # Build a map of other players (exclude troublemaker)
                    valid_targets = [p for p in idtoplayers.keys() if p != troublemaker_name and p not in {"table1", "table2", "table3"}]
                    emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]  # expand as needed
                    pick_map = {emoji_list[i]: valid_targets[i] for i in range(len(valid_targets))}

                    # Pick first player
                    first_choice = await discord_commands.send_dm_with_reactions(
                        ctx.bot, ctx, troublemaker_name,
                        f"You are the Troublemaker. Pick the first player to swap roles:\n" + 
                        "\n".join(f"{emoji} - {pick_map[emoji]}" for emoji in pick_map),
                        list(pick_map.keys())
                    )
                    first_player = pick_map[first_choice]

                    # Remove first player from map for second pick
                    second_pick_map = {e: p for e, p in pick_map.items() if p != first_player}

                    # Pick second player
                    second_choice = await discord_commands.send_dm_with_reactions(
                        ctx.bot, ctx, troublemaker_name,
                        f"Pick the second player to swap roles:\n" + 
                        "\n".join(f"{emoji} - {second_pick_map[emoji]}" for emoji in second_pick_map),
                        list(second_pick_map.keys())
                    )
                    second_player = second_pick_map[second_choice]

                    # Swap roles between first_player and second_player
                    first_obj = idtoplayers[first_player]
                    second_obj = idtoplayers[second_player]
                    first_role = first_obj.Role()
                    second_role = second_obj.Role()
                    first_obj.ChangeRole(second_role)
                    second_obj.ChangeRole(first_role)

                    await discord_commands.send_dm(ctx, troublemaker_name, f"You swapped roles of {first_player} and {second_player}.")

                elif rolenumber == 6:
                    obj = roletoplayers["Insomniac"]
                    insomniac_name = obj.ID()
                    insomniac_obj = idtoplayers[insomniac_name]
                    current_role = insomniac_obj.Role()

                    await discord_commands.send_dm(ctx, insomniac_name, f"You are the Insomniac. Your current role is {current_role}.")

                rolenumber += 1
            else:
                rolenumber += 1
        print("Done")
        await vote_players_out(ctx,Members, idtoplayers)

async def vote_players_out(ctx, Members, idtoplayers):
    member_list = []
    member_dic = {}
    for Member in Members:
        member_list.append(Member.name)
        member_dic[Member.name] = 0
    set_emoji_list = ["1️⃣" ,"2️⃣" ,"3️⃣" ,"4️⃣", "5️⃣"]
    new_emoji_list = set_emoji_list[0:len(Members)]
    for Member in Members:
        first_choice = await discord_commands.send_dm_with_reactions(ctx.bot, ctx, Member.name, f'Who do you want to vote for hehehe ahahahah{member_list}', new_emoji_list)
        print(first_choice)
        key = new_emoji_list.index(first_choice)
        print(key)
        member_dic[member_list[key]] += 1
    highest_vote = max(member_dic, key = member_dic.get)
    for member in member_list:
        obj = idtoplayers[member]
        await ctx.send(f"{member} is {obj.Role()}")
    await ctx.send(f"{highest_vote} Has been voted loser hahaaha") 


async def make_onuw(playerIDs, members, playerNames , ctx):
    random.seed()
    random.shuffle(playerIDs)
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
        FORBIDDEN = {"table1", "table2", "table3"}
        if x not in FORBIDDEN: 
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