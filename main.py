import random
import os
import discord
from discord.ext import commands
from player import Player
import onuw as onuw_file
import discord_commands
import flipseven
import time
import quiplash as quip

        
playerIds = []
members = []
playerNames = []
timeSinceLastMessage = time.time()
gamesrunning = []

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
    client = discord.Client(intents=intents)

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
        gamesrunning.append("onuw")
        await start(ctx)
        await onuw_file.make_onuw(playerIds, members, playerNames,ctx)

    @bot.command()
    async def seven(ctx):
        gamesrunning.append("seven")
        await start(ctx)
        await flipseven.setupflipseven(playerIds, playerNames, ctx)
    
    @bot.command()
    async def quiplash(ctx):
        gamesrunning.append("quiplash")
        await start(ctx)
        await quip.setupquiplash(playerIds, ctx)
    
    @bot.command()
    async def hit(ctx):
        if checkTime():
            await flipseven.drawcard(ctx)
    
    @bot.command()
    async def stay(ctx):
        if checkTime():
            await flipseven.passturn(ctx)
    
    @bot.command()
    async def freeze(ctx, name):
        await flipseven.freeze(ctx, name)
    
    @bot.command()
    async def flip3(ctx, name):
        await flipseven.flipthree(ctx, name)
    
    # makes it so all the arguments after ?answer are joined into one string
    @bot.command()
    async def answer(ctx, *answer):
        full_answer = " ".join(answer)
        await quip.answer(ctx, full_answer)
    
    # if we want to add other things we should store which games are running in main
    @bot.event
    async def on_reaction_add(reaction, user):
        if user != client.user:
            if "quiplash" in gamesrunning:
                await quip.newVote(reaction, user)
            elif "cah" in gamesrunning:
                await cah.dosomething()

        
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

        playerNames = [member.name for member in members]

        
    bot.run(TOKEN)

def checkTime():
    global timeSinceLastMessage
    if time.time() - timeSinceLastMessage >= 0.5:
        timeSinceLastMessage = time.time()
        return True
    else:
        return False
if __name__ == '__main__':
    main()
