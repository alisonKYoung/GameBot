import random
import os
import discord
from discord.ext import commands
from player import Player
import onuw as onuw_file
import cah as cah_file
import discord_commands
import flipseven
import time
import quiplash as quip
from classes import Game
import secrethitler as sh

        
timeSinceLastMessage = time.time()
gamesrunning = {}

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
        game = await start(ctx)
        setupGamesRunning("onuw", game)
        await onuw_file.make_onuw(game.playerIds, game.playerIds, list(i.name for i in game.playerIds),ctx)

    @bot.command()
    async def cah(ctx):
        game = await start(ctx)
        setupGamesRunning("cah", game)
        await cah_file.setupCAH(game)

    @bot.command()
    async def seven(ctx):
        game = await start(ctx)
        setupGamesRunning("seven", game)
        await flipseven.setupflipseven(game.playerIds, list(i.name for i in game.playerIds), ctx)
    
    @bot.command()
    async def quiplash(ctx):
        game = await start(ctx)
        setupGamesRunning("quiplash", game)
        await quip.setupquiplash(game)
    
    @bot.command()
    async def hitler(ctx):
        game = await start(ctx)
        setupGamesRunning("hitler", game)
        await sh.setupsh(game)

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
    
    @bot.command()
    async def nominate(ctx, nominee):
        await sh.game.nom(ctx, nominee)
    
    @bot.command()
    async def lockinvote(ctx):
        await sh.game.lockinvote(ctx.author.name)
    
    @bot.command()
    async def execute(ctx, victim):
        await sh.game.execute(ctx, victim)
    
    # if we want to add other things we should store which games are running in main
    @bot.event
    async def on_reaction_add(reaction, user):
        if not user.bot:
            if "quiplash" == gamesrunning[user.name]:
                await quip.newVote(reaction, user)
            elif "cah" == gamesrunning[user.name]:
                await cah_file.newVote(reaction, user)
        
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

        random.seed()

        playerIds = members[:]

        game = Game(ctx, playerIds)
        return game
    
    def setupGamesRunning(gameName, game):
        for i in game.playerIds:
            gamesrunning[i.name] = gameName

        
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
