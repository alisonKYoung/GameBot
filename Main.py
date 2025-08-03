import random
import os
import discord
from discord.ext import commands

class Player:
    def __init__(self, PlayerID, Role):
        self.player = PlayerID
        self.role = Role
    def Role(self):
        return(self.role)
    def ID(self):
        return str(self.player)
    def ChangeRole(self, Role):
        self.role = Role
        

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
        

print("____________________________STARTING___________________________________")

def main():

    file = open('token.txt','r')
    content = file.read()
    file.close()

    TOKEN = content

    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    intents.members = True

    bot = commands.Bot(command_prefix="?", intents=intents)

    # Dictionary to store voice lists
    user_voice_lists = {}

    async def get_voice_members(ctx):
        """Return members in the same voice channel as the user."""
        if ctx.author.voice:
            voice_channel = ctx.author.voice.channel
            return [m for m in voice_channel.members if not m.bot]
        return []

    async def send_dm(member, message):
        """Internal function to DM a user."""
        try:
            await member.send(message)
            return True
        except discord.Forbidden:
            return False

    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")

    @bot.command()
    async def start(ctx):
        members = await get_voice_members(ctx)
        if not members:
            await ctx.send("❌ You are not in a voice channel or no valid members found.")
            return

        # Store the list for later reference
        user_voice_lists[ctx.author.id] = members

        # Show the list
        response = "**Members in your call:**\n"
        for i, member in enumerate(members, start=1):
            response += f"{i}. {member.name}\n"

        playern = len(members)
        playerIDs = members[:]
        playerNames = [member.name for member in members]
        Roleskeep = ["Doppelganger","Werewolf","Werewolf2","Minion","Mason","Seer","Robber","Troublemaker","Drunk","Insomniac","Villager","Hunter","Tanner"]
        Roles = ["Doppelganger","Werewolf","Werewolf2","Minion","Mason","Seer","Robber","Troublemaker","Drunk","Insomniac","Villager","Hunter","Tanner"]
        playerIDtoOBJ = {}
        RolestoOBJ = {}
        m2 = False

        random.shuffle(playerIDs)
        random.shuffle(playerIDs)
        random.shuffle(playerIDs)
        random.shuffle(Roles)
        random.shuffle(Roles)
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
            await send_dm(members[i],"The Game Has Started!")
            await send_dm(members[i],"You are the " + obj.Role())
            await send_dm(members[i],"The Night phase is starting...")

        #perform_night_actions(playerIDtoOBJ, RolestoOBJ, Roles)

    bot.run(TOKEN)

if __name__ == '__main__':
    main()
