import random
import discord_commands
from collections import deque
import time

class QuiplashPlayer():
    def __init__(self, playerId):
        self.playerId = playerId
        self.points = 0
        self.questions = []
        self.questionsAnswered = 0
    # getPoints is used for sorting players by num of points
    def getPoints(self):
        return self.points

class Game():
    def __init__(self):
        self.players = {}
        self.numQuestions = 0
        self.roundNum = 0
        self.questions = []
        self.allQuestions = []
        self.playerNames = []
        self.playerObjects = []
        self.basePointsPerVote = 500
        self.baseWinnerBonus = 100
        self.pointsPerVote = 0
        self.winnerBonus = 0
        self.votingQuestionNum = 0
        self.insertNameString = "[insert-name-here]"
    def distributeQuestions(self):
        temp = 0
        for q in self.questions:
            # set up randomly inserting names for however many players there are
            rplayers = []
            for i in range(q.text.count(self.insertNameString)):
                randomPlayer = random.choice(self.playerNames)
                while randomPlayer in rplayers:
                    randomPlayer = random.choice(self.playerNames)
                rplayers.append(randomPlayer)
            q.replaceName(self.insertNameString, rplayers)

            # make the first and second players in playerNames the people who answer this question
            q.players.append(self.playerNames[0])
            self.players[self.playerNames[0]].questions.append(q.text)
            q.players.append(self.playerNames[1])
            self.players[self.playerNames[1]].questions.append(q.text)
            # make it so they can't vote on this question
            q.alreadyVoted = [self.playerNames[0], self.playerNames[1]]
            # rotate the two players to the back of the list
            # for odd number of players ensures they all get two questions
            d = deque(self.playerNames)
            d.rotate(2)
            self.playerNames = list(d)
            # special code for even number of players
            # if it has gone through half the questions (meaning each player has gotten one question)
            # it shuffles the players
            temp += 1
            if self.numQuestions % 2 == 0 and temp == self.numQuestions / 2:
                random.seed()
                random.shuffle(self.playerNames)
    
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
    def replaceName(self, replaceString, *names):
        for name in names:
            self.text.replace(replaceString, name, 1)

# only one global variable needed
game = Game()

async def setupquiplash(playerIds, ctx):
    global game
    game = Game()
    await ctx.send(f"now watch me quip, now watch me nae nae")
    for i in playerIds:
        # set up game.players dictionary using the player names as keys
        # afaik we only need the player names and the ids are useless
        game.players[i.name] = QuiplashPlayer(i.id)
        game.playerNames.append(i.name)
    # because each player gets two questions and each question has two players
    # the number of questions is just going to be the number of players
    game.numQuestions = len(playerIds)
    with open("quiplashquestions.txt", "r") as f:
        # create a list where each item is a line in the file
        game.allQuestions = list(map(str.rstrip, f.readlines()))
    random.seed()
    random.shuffle(game.allQuestions)
    # this is important
    # make it so that instead of bouncing ctx around all the functions
    # we save it in one variable
    # so the events that are from dms can still use the main channel
    game.channelContext = ctx
    await nextRound(ctx)

async def nextRound(ctx):
    global game
    await game.newRound()
    if game.roundNum > 3:
        return
    await ctx.send(f"round {game.roundNum}")
    for i in range(game.numQuestions):
        game.questions.append(Question(game.allQuestions[i]))
    # make it so the questions won't show up again
    game.allQuestions = game.allQuestions[game.numQuestions:]
    game.distributeQuestions()

    await ctx.send(f"sending question 1 now")
    # send each player their first question
    for name, player in game.players.items():
        await discord_commands.send_dm(ctx, name, player.questions[0])

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