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
    def distributeQuestions(self):
        temp = 0
        for q in self.questions:
            q.players.append(self.playerNames[0])
            self.players[self.playerNames[0]].questions.append(q.text)
            q.players.append(self.playerNames[1])
            self.players[self.playerNames[1]].questions.append(q.text)
            q.alreadyVoted = [self.playerNames[0], self.playerNames[1]]
            d = deque(self.playerNames)
            d.rotate(2)
            self.playerNames = list(d)
            temp += 1
            if self.numQuestions % 2 == 0 and temp%2 == 0:
                random.seed()
                random.shuffle(self.playerNames)
    
    async def sendWin(self):
        winner = max(self.players, key = lambda k: self.players[k].points)
        await self.channelContext.send(f"{winner} won")

    async def newRound(self):
        self.roundNum += 1
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
        for name, answer in self.playerAnswers.items():
            if answer == messageText:
                self.votesTally[name] += 1
                self.votes += 1
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

game = Game()

async def setupquiplash(playerIds, ctx):
    global game
    game = Game()
    await ctx.send(f"now watch me quip, now watch me nae nae")
    for i in playerIds:
        game.players[i.name] = QuiplashPlayer(i.id)
        game.playerNames.append(i.name)
    game.numQuestions = len(playerIds)
    with open("quiplashquestions.txt", "r") as f:
        game.allQuestions = list(map(str.rstrip, f.readlines()))
    random.seed()
    random.shuffle(game.allQuestions)
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
    game.allQuestions = game.allQuestions[game.numQuestions:]
    game.distributeQuestions()

    await ctx.send(f"sending question 1 now")

    for name, player in game.players.items():
        await discord_commands.send_dm(ctx, name, player.questions[0])

async def answer(ctx, answer):
    global game
    player = game.players[ctx.author.name]
    if player.questionsAnswered < 2:
        answeredQuestion = player.questions[player.questionsAnswered]
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

async def setupVote():
    global game
    await game.channelContext.send("------------------------------")
    await game.channelContext.send("Vote for your favorite answer using 👍")
    await game.sendVote()

async def newVote(reaction, user):
    global game
    if str(reaction.emoji) == "👍":
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
    players_copy = dict(game.players)
    for i in range(len(game.players)):
        name = max(players_copy, key = lambda k: players_copy[k].points)
        await game.channelContext.send(f"{name}: {str(game.players[name].points)}")
        del players_copy[name]
    await nextRound(game.channelContext)