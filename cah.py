import random
import discord_commands
from collections import deque
import time
import discord

class CAHPlayer():
    def __init__(self, playerId, name):
        self.playerId = playerId
        self.name = name
        self.points = 0
        self.white_cards = []
    # getPoints is used for sorting players by num of points
    def getPoints(self):
        return self.points

class Game():
    def __init__(self):
        self.players = {}
        self.roundNum = 0
        self.black_cards = []
        self.playerNames = []
        self.playerObjects = []
        self.insertNameString = "[insert-name-here]"
    async def distributeQuestions(self):
        answers = {}
        emo = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        print(self.playerObjects)
        black_card_text = self.black_cards[self.roundNum]
        await self.channelContext.send(black_card_text)
        for player in self.playerObjects:
            name = player.name
            for card in player.white_cards:
                await discord_commands.send_dm(self.channelContext, name, card)
            first_choice = await discord_commands.send_dm_with_reactions(self.channelContext.bot, self.channelContext, name, "Which one do you want to use?", emo)
            index_map = {"1️⃣": 0, "2️⃣": 1, "3️⃣": 2, "4️⃣": 3, "5️⃣": 4}
            key = index_map.get(first_choice)
            chosen_card = player.white_cards[key]
            filled_card = black_card_text.replace("___", chosen_card)
            answers[player] = filled_card
        return answers


    async def sendWin(self):
        # finds player who has the most points
        winner = max(self.players, key = lambda k: self.players[k].points)
        await self.channelContext.send(f"{winner} won")

    # resets everything
    async def newRound(self):
        self.roundNum += 1
        # only plays 3 rounds
        if self.roundNum == 4:
            await self.sendWin()
            return
        self.questions = []
        for name, p in self.players.items():
            p.questions = []
            p.questionsAnswered = 0
        self.pointsPerVote = self.basePointsPerVote * self.roundNum
        self.winnerBonus = self.baseWinnerBonus * self.roundNum
        self.votingQuestionNum = 0
        random.seed()
        random.shuffle(self.playerNames)
    
    async def sendVote(self):
        q = self.questions[self.votingQuestionNum]
        await self.channelContext.send(f"Question: **{q.text}**")
        time.sleep(0.5)
        await self.channelContext.send(q.playerAnswers[q.players[0]])
        time.sleep(0.5)
        await self.channelContext.send("vs")
        time.sleep(0.5)
        await self.channelContext.send(q.playerAnswers[q.players[1]])
    
    def calcPoints(self):
        for q in self.questions:
            checktie = 0
            for player, value in q.votesTally.items():
                self.players[player].points += value * self.pointsPerVote
                checktie = value
            if q.votes / 2 != checktie:
                # for getting the key with the max value in a dictionary, you have to do this
                winner = max(q.votesTally, key = q.votesTally.get)
                self.players[winner].points += self.winnerBonus
    
    def checkAllDone(self):
        for name, player in self.players.items():
            if player.questionsAnswered < 2:
                return False
        return True

class Question():
    def __init__(self, text):
        self.text = text
        self.players = []
        self.playerAnswers = {}
        self.votes = 0
        self.alreadyVoted = []
        self.votesTally = {}
    def addVote(self, messageText, user):
        # unfortunately we have to loop through the dictionary to find the value that matches
        for name, answer in self.playerAnswers.items():
            if answer == messageText:
                self.votesTally[name] += 1
                self.votes += 1
                # make it so they can't vote again
                self.alreadyVoted.append(user.name)
                break
        return self.votes
    #this won't do anything for now because discord doesn't track removing reactions well
    def removeVote(self, messageText, user):
        for name, answer in self.playerAnswers.items():
            if answer == messageText and not user.name in self.players:
                self.votesTally[name] -= 1
                self.votes -= 1
                self.alreadyVoted.remove(user.name)
                break
    # takes in a list of names and replaces each instance of the replacement string in self.text with a name
    def replaceName(self, replaceString, names):
        for name in names:
            self.text = self.text.replace(replaceString, name, 1)

# only one global variable needed
game = Game()

async def setupCAH(playerIds, ctx):
    global game
    game = Game()
    await ctx.send(f"Cards Against Humanity!!!")
    for i in playerIds:
        newplayer = CAHPlayer(i.id,i.name) 
        game.playerObjects.append(newplayer)
        # set up game.players dictionary using the player names as keys
        # afaik we only need the player names and the ids are useless
        game.players[i.name] = newplayer
        game.players[i.name].nickname = i.display_name
        game.playerNames.append(i.name)
    # because each player gets two questions and each question has two players
    # the number of questions is just going to be the number of players
    game.numQuestions = len(playerIds)
    with open("cah_black_cards.txt", "r") as f:
        # create a list where each item is a line in the file
        game.black_cards = list(map(str.rstrip, f.readlines()))
    random.seed()
    random.shuffle(game.black_cards)
    white_cards = []
    with open("cah_white_cards.txt", "r") as f:
        # create a list where each item is a line in the file  
        white_cards = list(map(str.rstrip, f.readlines()))
    random.shuffle(white_cards)
    for player in game.playerObjects:
        player.white_cards = []
        for i in range(5):
            card = white_cards.pop(0)
            player.white_cards.append(card)
    # this is important
    # make it so that instead of bouncing ctx around all the functions
    # we save it in one variable
    # so the events that are from dms can still use the main channel
    game.channelContext = ctx
    await nextRound(ctx)

async def nextRound(ctx):
    global game
    #await game.newRound()
    #if game.roundNum > 3:
    #    return
    #await ctx.send(f"round {game.roundNum}")
    #for i in range(game.numQuestions):
    #    game.questions.append(Question(game.allQuestions[i]))
    # make it so the questions won't show up again
    #game.allQuestions = game.allQuestions[game.numQuestions:]
    answers = await game.distributeQuestions()
    print(answers)
    for x in answers:
        await ctx.send(answers[x])

    #await ctx.send(f"sending question 1 now")
    # send each player their first question
    #for name, player in game.players.items():
    #    await discord_commands.send_dm(ctx, name, player.questions[0])

async def answer(ctx, answer):
    global game
    # ctx.author.name will get the player name
    player = game.players[ctx.author.name]
    if player.questionsAnswered < 2:
        # player.questions is a list so we use player.questionsAnswered as an index
        answeredQuestion = player.questions[player.questionsAnswered]
        # find the question in game.questions
        for question in game.questions:
            if question.text == answeredQuestion:
                question.playerAnswers[ctx.author.name] = answer
                question.votesTally[ctx.author.name] = 0
                break
        game.players[ctx.author.name].questionsAnswered+=1
        if player.questionsAnswered < 2:
            await discord_commands.send_dm(game.channelContext, ctx.author.name, player.questions[1])
        else: 
            await discord_commands.send_dm(game.channelContext, ctx.author.name, "all done now look at you go")
    if game.checkAllDone():
        await setupVote()

# honestly we could probably combine this with game.sendVote() but I'm too lazy
async def setupVote():
    global game
    await game.channelContext.send("------------------------------")
    await game.channelContext.send("Vote for your favorite answer using 👍")
    await game.sendVote()

# will trigger when any reaction is added
async def newVote(reaction, user):
    global game
    # will only do something if the reaction is a thumbs up
    if str(reaction.emoji) == "👍":
        # if the user hasn't already voted and is not one of the people who answered the question
        if not user.name in game.questions[game.votingQuestionNum].alreadyVoted:
            numVotes = game.questions[game.votingQuestionNum].addVote(reaction.message.content, user)
            if numVotes == len(game.players) - 2:
                game.votingQuestionNum += 1
                if game.votingQuestionNum == len(game.questions):
                    await tallyPoints()
                else:
                    await setupVote()

async def tallyPoints():
    global game
    game.calcPoints()
    await game.channelContext.send("---------------leaderboard---------------")
    # have to make a copy so we can delete items from the copy while we're looping
    players_copy = dict(game.players)
    for i in range(len(game.players)):
        name = max(players_copy, key = lambda k: players_copy[k].points)
        await game.channelContext.send(f"{name}: {str(game.players[name].points)}")
        del players_copy[name]
    await nextRound(game.channelContext)