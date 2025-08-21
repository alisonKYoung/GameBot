import random
import discord_commands
from collections import deque
import time
import discord
from classes import Game, Player

class CAHPlayer(Player):
    def __init__(self, playerId, name, nickname):
        super().__init__(playerId, name, nickname)
        self.points = 0
        self.white_cards = []
    def getPoints(self):
        return self.points

class CAHGame(Game):
    def __init__(self, baseGame):
        super().__init__(baseGame.channelContext, baseGame.playerIds)
        self.roundNum = 0
        self.black_cards = []
        self.white_cards = []
        self.turn = 0
        self.answers = {}
        self.insertNameString = "[insert-name-here]"

    def createPlayers(self, PlayerClass):
        super().createPlayers(PlayerClass)
        self.playorder = self.playerNames
        random.seed()
        random.shuffle(self.playorder)

    async def distributeQuestions(self):
        answers = {}
        emo = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        print(self.playerNames)
        black_card_text = self.black_cards[self.roundNum]
        await self.channelContext.send(black_card_text)
        for name, player in self.players.items():
            if name == self.playorder[self.turn]:
                await discord_commands.send_dm(self.channelContext, name, "YOUR WILL JUDGE")    
            else:
                for card in player.white_cards:
                    await discord_commands.send_dm(self.channelContext, name, card)
                first_choice = await discord_commands.send_dm_with_reactions(self.channelContext.bot, self.channelContext, name, "Which one do you want to use?", emo)
                index_map = {"1️⃣": 0, "2️⃣": 1, "3️⃣": 2, "4️⃣": 3, "5️⃣": 4}
                key = index_map.get(first_choice)
                chosen_card = player.white_cards[key]
                player.white_cards.remove(chosen_card)
                filled_card = black_card_text.replace("___", chosen_card)
                answers[player] = filled_card
                if len(self.white_cards) >= 0:
                    for name, player in game.players.items():
                        card = self.white_cards.pop(0)
                        player.white_cards.append(card)
        self.black_cards.remove(black_card_text)
        self.answers = answers
        return answers
    
    # resets everything
    async def newRound(self):
        if self.turn == len(self.playorder) - 1:
            self.turn = 0
        else:
            self.turn += 1
        await nextRound()


async def setupCAH(g):
    global game
    game = CAHGame(g)
    await game.channelContext.send(f"Cards Against Humanity!!!")
    game.createPlayers(CAHPlayer)
    # because each player gets two questions and each question has two players
    # the number of questions is just going to be the number of players
    game.numQuestions = len(game.playerIds)
    with open("cah_black_cards.txt", "r") as f:
        # create a list where each item is a line in the file
        game.black_cards = list(map(str.rstrip, f.readlines()))
    random.seed()
    random.shuffle(game.black_cards)
    white_cards = []
    with open("cah_white_cards.txt", "r") as f:
        # create a list where each item is a line in the file  
        game.white_cards = list(map(str.rstrip, f.readlines()))
    random.shuffle(white_cards)
    for name, player in game.players.items():
        player.white_cards = []
        for i in range(5):
            card = game.white_cards.pop(0)
            player.white_cards.append(card)
    await nextRound()

async def nextRound():
    global game
    await tallyPoints()
    answers = await game.distributeQuestions()
    await game.channelContext.send("Everybody shut up and listen")
    await discord_commands.send_dm(game.channelContext, game.playorder[game.turn], "Time to read loser")
    for x in answers:
        await discord_commands.send_dm(game.channelContext, game.playorder[game.turn], answers[x])

# will trigger when any reaction is added
async def newVote(reaction, user):
    global game
    if str(reaction.emoji) == "👍":
        if user.name == game.playorder[game.turn]:  
            for key, value in game.answers.items():
                if reaction.message.content == value:
                    print(key)
                    #for key, value in game.answers.items():
                    #    await game.channelContext.send(value)
                    await game.channelContext.send(f"{key.name} Won this round!")
                    key.points += 1
                    await game.newRound()

async def tallyPoints():
    global game
    await game.channelContext.send("---------------leaderboard---------------")
    for name, player in game.players.items():
        await game.channelContext.send(f"{name} has {player.getPoints()}")