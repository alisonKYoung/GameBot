import random
import os
import discord
from discord.ext import commands
from player import Player
import onuw as onuw_file
import discord_commands
import flipseven

        
playerIds = []
members = []
playerNames = []       

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


    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")

    @bot.command()
    async def onuw(ctx):
        await start(ctx)
        await onuw_file.make_onuw(playerIds, members, playerNames,ctx)

    @bot.command()
    async def seven(ctx):
        await start(ctx)
        await flipseven.setupflipseven(playerIds, playerNames, ctx)
    
    @bot.command()
    async def hit(ctx):
        await flipseven.drawcard(ctx)
    
    @bot.command()
    async def stay(ctx):
        await flipseven.passturn(ctx)

        
    async def start(ctx):
        global playerIds, members, playerNames
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

        random.seed()

        playerIds = members[:]
        random.shuffle(playerIds)

        playerNames = [member.name for member in members]

        

    bot.run(TOKEN)

if __name__ == '__main__':
    main()
