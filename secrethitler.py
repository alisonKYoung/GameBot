import random
from discord_commands import send_dm, send_dm_with_reactions
from classes import Game, Player
from math import floor
from collections import deque
from discord.utils import get
import time

class SecretHitlerPlayer(Player):
    def __init__(self, playerId, name, nickname):
        super().__init__(playerId, name, nickname)
        self.role = "Normal Not Nazi Person"
        self.team = "Liberal"
        self.dead = False

class SecretHitlerGame(Game):
    def __init__(self, baseGame):
        super().__init__(baseGame.channelContext, baseGame.playerIds)

        self.numPlayers = len(self.playerIds)
        self.libPolicies = 0
        self.fasPolicies = 0
        self.electionFails = 0
        self.fascists = []
        self.hitler = ""
        self.electionTracker = ["0 fails!", "1 fail :(", "2 fails :((", "reveal and enact!!!"]
        self.termLimited = []
        self.shuffleDeck()
        self.execution = False
        self.election = False
    
    def shuffleDeck(self):
        self.deck = []
        for i in range(6):
            self.deck.append("Liberal Policy")
        for i in range(11):
            self.deck.append("Fascist Policy")
        random.seed()
        random.shuffle(self.deck)

    def distributeRoles(self):
        numFascists = round(self.numPlayers * 2/5)
        random.seed()
        self.fascists = random.sample(self.playerNames, numFascists)
        self.hitler = random.choice(self.fascists)
        for f in self.fascists:
            self.players[f].team = "Fascist"
            self.players[f].role = "Not Hitler"
        self.players[self.hitler].role = "Hitler"
        self.chooseBoard()
    
    def chooseBoard(self):
        boards = [
            ["0 fascist policies", "Nothing", "Nothing", "Policy Peek", "Execution", "Execution", "bad things happen"],
            ["None", "Investigate Loyalty", "Special Election", "Execution", "Execution", "bad things happen"]
        ]
        self.fboard = boards[floor((self.numPlayers - 5)/2)]
        self.lboard = ["0 policies", "1 policy", "2 policies", "3 policies", "4 policies", "good things happen"]

    async def messageRoles(self):
        for p in self.playerNames:
            message = f"Your party: {self.players[p].team}\nYour role: {self.players[p].role}"
            await send_dm(self.channelContext, p, message)
            if self.numPlayers <= 6:
                if p in self.fascists:
                    await send_dm(self.channelContext, p, f"The fascists are: {" ".join(self.fascists)}")
            else:
                if p in self.fascists and p != self.hitler:
                    await send_dm(self.channelContext, p, f"The fascists are: {" ".join(self.fascists)}\nHitler is: {self.hitler}")
    
    def formatTracker(self, tracker, boldIndex):
        t = []
        for i in range(len(tracker)):
            stripped = tracker[i].replace("~", "").replace("*", "")
            if i < boldIndex:
                stripped = f"~~{stripped}~~"
            elif i == boldIndex:
                stripped = f"**{stripped}**"
            t.append(stripped)
        trackerString = " \|\| ".join(t)
        return trackerString

    async def sendBoardState(self):
        lboardstate = "Liberal Board: " + self.formatTracker(self.lboard, self.libPolicies)
        fboardstate = "Fascist Board: " + self.formatTracker(self.fboard, self.fasPolicies)
        etrackerstate = "Election Tracker: " + self.formatTracker(self.electionTracker, self.electionFails)
        deckstate = "Cards in deck: " + str(len(self.deck))
        message = f"Boardstate:\n{lboardstate}\n{fboardstate}\n{etrackerstate}\n{deckstate}"
        await self.channelContext.send(message)
    
    async def newTurn(self):
        await self.sendBoardState()
        await self.channelContext.send(f"Next presidents: {" ".join(self.playerNames)}")
        await self.channelContext.send(f"President: {self.president}\nUse ?nominate [name] to nominate someone for chancellor")
        self.election = True

    def setPresident(self):
        self.president = self.playerNames[0]
        self.rotateTurnOrder()
    
    def rotateTurnOrder(self):
        d = deque(self.playerNames)
        d.rotate(1)
        self.playerNames = list(d)
    
    async def setup(self):
        self.createPlayers(SecretHitlerPlayer)
        self.distributeRoles()
        await self.messageRoles()
        self.setPresident()
        await self.newTurn()
    
    async def nom(self, ctx, nominee):
        if ctx.author.name != self.president or not self.election or nominee == self.president:
            return
        if not nominee in self.termLimited:
            if not self.players[nominee].dead:
                self.cNom = nominee
                secondLine = f"{self.president}, please send ?lockinvote when all votes are in and ready"
                self.nomMessage = await self.channelContext.send(f"React to this message with a 👎 for nein and a 👍 for ja\n{secondLine}")
                await self.nomMessage.add_reaction("👍")
                await self.nomMessage.add_reaction("👎")
            else:
                await self.channelContext.send(f"w-where's {nominee}? *cough* what? she's dead. we're reading her will")
        else:
            await self.channelContext.send("They were president/chancellor last round")
    
    async def lockinvote(self, username):
        if username == self.president and self.election:
            reaction_counts = {}
            self.nomMessage = await self.channelContext.fetch_message(self.nomMessage.id)
            for reaction in self.nomMessage.reactions:
                reaction_counts[str(reaction.emoji)] = reaction.count

            ja = reaction_counts["👍"]
            nein = reaction_counts["👎"]
            if ja > nein:
                await self.channelContext.send("you did not fail")
                self.chancellor = self.cNom
                self.termLimited = []
                # self.termLimited.append(self.president)
                # self.termLimited.append(self.chancellor)
                self.electionFails = 0
                if await self.checkWin():
                    return
                self.election = False
                await self.lawmake()
            else:
                await self.channelContext.send("wow you failed a vote")
                self.electionFails += 1
                if self.electionFails == 3:
                    await self.enactTop()
                    self.electionFails = 0
                self.setPresident()
                self.election = False
                await self.newTurn()
    
    async def lawmake(self):
        cards = self.deck[:3]
        self.deck = self.deck[3:]
        if len(self.deck) < 3:
            await self.channelContext.send("Reshuffling deck")
            self.shuffleDeck()
        presMessage = f"Card 1: {cards[0]}\nCard 2: {cards[1]}\nCard 3: {cards[2]}\nWhich card do you want to discard?"
        reactionsList = ["1️⃣", "2️⃣", "3️⃣"]
        choice = await send_dm_with_reactions(self.channelContext.bot, self.channelContext, self.president, presMessage, reactionsList)
        index = reactionsList.index(choice)
        cards.pop(index)
        await self.channelContext.send("The president has discarded a card")
        
        chanMessage = f"Card 1: {cards[0]}\nCard 2: {cards[1]}\nWhich card do you want to play?"
        choice = await send_dm_with_reactions(self.channelContext.bot, self.channelContext, self.chancellor, chanMessage, ["1️⃣", "2️⃣"])
        index = reactionsList.index(choice)
        playedCard = cards[index]
        await self.channelContext.send("The chancellor played a...")
        time.sleep(1)
        await self.channelContext.send(playedCard)

        if playedCard == "Liberal Policy":
            self.libPolicies += 1
        else:
            self.fasPolicies += 1
            cont = await self.doFascism()
            if not cont:
                return
        
        if await self.checkWin():
            return

        self.setPresident()
        await self.newTurn()
    
    async def checkWin(self):
        if (self.fasPolicies >= 3 and self.hitler == self.chancellor and self.election) or self.fasPolicies == 6:
            await self.channelContext.send("Fascists win!")
            await self.channelContext.send(f"The fascists were: {" ".join(self.fascists)}\nHitler was: {self.hitler}")
            return True
        if self.libPolicies == 5 or self.players[self.hitler].dead:
            await self.channelContext.send("Liberals win!")
            await self.channelContext.send(f"The fascists were: {" ".join(self.fascists)}\nHitler was: {self.hitler}")
            return True
        return False

    async def enactTop(self):
        card = self.deck.pop(0)
        await self.channelContext.send("Playing the top card...")
        time.sleep(1)
        await self.channelContext.send(f"A {card} was enacted")
        if card == "Liberal Policy":
            self.libPolicies += 1
        else:
            self.fasPolicies += 1
        
        if await self.checkWin():
            return
    
    async def doFascism(self):
        if self.fasPolicies == 6:
            return True
        fascism = self.fboard[self.fasPolicies]
        await self.channelContext.send(f"Because a fascist policy was enacted, the president gets to do {fascism}")
        if fascism == "Nothing":
            return True
        elif fascism == "Policy Peek":
            topCards = self.deck[:3]
            presMessage = f"Top cards on the deck:\nCard 1: {topCards[0]}\nCard 2: {topCards[1]}\nCard 3: {topCards[2]}\nreact with 👍 when done looking"
            await send_dm_with_reactions(self.channelContext.bot, self.channelContext, self.president, presMessage, ["👍"])
            return True
        elif fascism == "Execution":
            await self.channelContext.send("Send ?execute [who to kill]")
            self.execution = True
            return False
    
    async def execute(self, ctx, victim):
        if self.execution and ctx.author.name == self.president:
            if victim in self.playerNames and not self.players[victim].dead:
                self.players[victim].dead = True
                self.playerNames.remove(victim)
                await self.channelContext.send("pew pew")
                if self.players[victim].role == "Hitler":
                    await self.channelContext.send("They were hitler")
                    if await self.checkWin():
                        return
                else:
                    await self.channelContext.send("They were not hitler")
                self.setPresident()
                self.newTurn()
                self.execution = False

async def setupsh(g):
    global game
    game = SecretHitlerGame(g)
    await game.setup()