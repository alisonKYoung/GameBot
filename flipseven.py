import random
import time

players = {}
deck = []
turnOrder = []
turnNum = 0
roundNum = 1
currentPlayer = ""
emoji_deck = {"1_":1401823011325218836,"2_":1401826857589932042,"3_":1401826872236576880,"4_":1401826887373951046,
              "5_":1401826981041143828,"6_":1401826995309908121,"7_":1401827010875097278,"8_":1401827021797199943,
              "9_":1401827036560883813,"10_":1401827050762801235,"11_":1401827064725639180,"12_":1401827076956225557,
              "0_":1401827088037711932}


class FlipSevenPlayer():
    def __init__(self, PlayerID):
        self.player = PlayerID
        self.inventory = []
        self.passTurn = False
        self.busted = False
        self.points = 0

class Card():
    def __init__(self, value, dupebad=False, modifier=False):
        self.value = value
        self.dupebad = dupebad
        self.modifier = modifier
        if value.isdigit():
            self.point_total = int(value)
        else:
            self.point_total = 0
    def get_emoji_string(self, ctx, bot, value):
        number = str(value) + "_"
        id = emoji_deck[number]
        if self.modifier:
            emoji_name += "-modifier"
        return f"<:{number}:{id}>"

async def calcPlayerPoints(ctx):
    global players
    for pid, player in players.items():
        points = 0
        if not player.busted:
            for card in player.inventory:
                points += card.point_total
        else:
            player.busted = False
        player.points += points
        player.passTurn = False
        player.inventory = []
        await ctx.send(f"{player.name} got {points} more points, bring them to a total of {player.points}")

async def setupflipseven(playerIDs, playerNames, ctx):
    global deck, player, turnOrder
    await ctx.send(f"flip7flip7flip7flip7flip7flip7flip7")
    for i in range(len(playerIDs)):
        players[playerIDs[i].id] = FlipSevenPlayer(playerIDs[i].id)
        players[playerIDs[i].id].name = playerNames[i]
    deck.append(Card("0", dupebad=True))
    for i in range(13):
        for j in range(i):
            deck.append(Card(str(i), dupebad=True))
    random.seed()
    random.shuffle(deck)
    turnOrder = [playerNames[i] for i in range(len(playerNames))]
    random.seed()
    random.shuffle(turnOrder)
    await ctx.send("turn order")
    for player in turnOrder:
        time.sleep(0.5)
        await ctx.send(player)
    # message = f"{deck[0].get_emoji_string(ctx)} this is a {deck[0].value}"
    # await ctx.send(message)
    await playflipseven(ctx)
    

async def playflipseven(ctx):
    global turnNum, roundNum, turnOrder, currentPlayer
    if turnNum == 0:
        await ctx.send(f"round {roundNum}")
    getCurrentPlayer()
    if not currentPlayer.passTurn and not currentPlayer.busted:
        await ctx.send(f"what do you want to do {turnOrder[turnNum % len(turnOrder)]}?")
    else:
        turnNum += 1
        await playflipseven(ctx)

async def drawcard(ctx):
    global turnNum, deck, players
    if ctx.author.name == turnOrder[turnNum % len(turnOrder)]:
        await ctx.send(f"you drew a {deck[0].value} {deck[0].get_emoji_string(ctx, ctx.bot,deck[0].value)}")
        if deck[0].dupebad:
            for card in players[ctx.author.id].inventory:
                if card.value == deck[0].value:
                    await ctx.send(f"you busted :(")
                    for pid, player in players.items():
                        if player.name == turnOrder[turnNum % len(turnOrder)]:
                            player.busted = True
                    allBusted = True
                    turnNum+=1
                    for pid, player in players.items():
                        if not player.busted and not player.passTurn:
                            allBusted = False
                            break
                    if allBusted:
                        await ctx.send("everyone is out now")
                        roundNum+=1
                        turnNum = 0
                        await calcPlayerPoints(ctx)
        if not players[ctx.author.id].busted:
            players[ctx.author.id].inventory.append(deck.pop(0))
            inventory_string = ", ".join([card.value for card in players[ctx.author.id].inventory])
            await ctx.send(f"you now have: {inventory_string}")
            turnNum+=1
    else:
        await ctx.send("not you")
    await playflipseven(ctx)

async def passturn(ctx):
    global turnNum, players, currentPlayer, roundNum
    getCurrentPlayer()
    if ctx.author.name == turnOrder[turnNum % len(turnOrder)]:
        for pid, player in players.items():
            if player.name == turnOrder[turnNum % len(turnOrder)]:
                player.passTurn = True
                currentPlayer = player
        allPassed = True
        for pid, player in players.items():
            if not player.passTurn and not player.busted:
                allPassed = False
                break
        turnNum += 1

        inventory_string = ", ".join([card.value for card in currentPlayer.inventory])
        await ctx.send(f"you still have: {inventory_string}")

        if allPassed:
            roundNum+=1
            turnNum = 0
            await calcPlayerPoints(ctx)
    else:
        await ctx.send("not you")
    await playflipseven(ctx)

def getCurrentPlayer():
    global turnNum, turnOrder, currentPlayer, players
    for pid, player in players.items():
        if player.name == turnOrder[turnNum % len(turnOrder)]:
            currentPlayer = player