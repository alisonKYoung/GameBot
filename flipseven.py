import random
import time
from collections import deque
import threading

players = {}
deck = []
turnOrder = []
turnNum = 0
roundNum = 1
currentPlayer = ""
worstcasescenario = False
emoji_deck = {"1_":1401823011325218836,"2_":1401826857589932042,"3_":1401826872236576880,"4_":1401826887373951046,
              "5_":1401826981041143828,"6_":1401826995309908121,"7_":1401827010875097278,"8_":1401827021797199943,
              "9_":1401827036560883813,"10_":1401827050762801235,"11_":1401827064725639180,"12_":1401827076956225557,
              "0_":1401827088037711932, "freeze_":1402175827327717417, "2_modifier":1402174857696907264, 
              "4_modifier":1402175105731395714, "6_modifier":1402175292155498497, "8_modifier":1402177077699940373,
              "10_modifier":1402175605465682050,"flip3_":1402175759862464634,"secondchance_":1402175877420286012,
              "timestwo_":1402175922060398724}


class FlipSevenPlayer():
    def __init__(self, PlayerID):
        self.player = PlayerID
        self.inventory = []
        self.passTurn = False
        self.busted = False
        self.points = 0
        self.seven = False

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
        emoji_name = str(value) + "_"
        if self.modifier:
            emoji_name += "modifier"
        id = emoji_deck[emoji_name]
        return f"<:{emoji_name}:{id}>"

async def calcPlayerPoints(ctx):
    global players
    for pid, player in players.items():
        points = 0
        mod_total = 0
        times_two = False
        if not player.busted:
            for card in player.inventory:
                if card.modifier:
                    mod_total += card.point_total
                else:
                    points += card.point_total
                if card.value == "timestwo":
                    times_two = True
            if times_two:
                points *= 2
            points += mod_total
        else:
            player.busted = False
        player.points += points
        player.passTurn = False
        player.seven = False
        player.inventory = []
        await ctx.send(f"{player.name} got {points} more points, bring them to a total of {player.points}")

async def setupflipseven(playerIDs, playerNames, ctx):
    global deck, player, turnOrder, turnNum, roundNum
    turnNum = 0
    roundNum = 1
    await ctx.send(f"flip7flip7flip7flip7flip7flip7flip7")
    for i in range(len(playerIDs)):
        players[playerIDs[i].name] = FlipSevenPlayer(playerIDs[i].id)
        players[playerIDs[i].name].name = playerNames[i]
    setupdeck()
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
    

async def playflipseven(ctx, notyou=False):
    global turnNum, roundNum, turnOrder, currentPlayer
    if turnNum == 0:
        await ctx.send(f"round {roundNum}")
        if roundNum > 1 and not notyou:
            rotateTurnOrder()
    getCurrentPlayer()
    if not currentPlayer.passTurn and not currentPlayer.busted and not currentPlayer.seven:
        await ctx.send(f"what do you want to do {turnOrder[turnNum % len(turnOrder)]}?")
    else:
        turnNum += 1
        await playflipseven(ctx)

async def drawcard(ctx):
    global turnNum, deck, players, roundNum
    if ctx.author.name == turnOrder[turnNum % len(turnOrder)]:
        schance = False
        if len(deck) == 0:
            await ctx.send("shuffling...")
            setupdeck()
            time.sleep(0.5)
        await ctx.send(f"you drew {deck[0].get_emoji_string(ctx, ctx.bot,deck[0].value)} ({deck[0].value})")
        if deck[0].dupebad:
            for card in players[ctx.author.name].inventory:
                if card.value == deck[0].value and not card.modifier:
                    if not "secondchance" in [card.value for card in players[ctx.author.name].inventory]:
                        await ctx.send(f"you busted :(")
                        players[ctx.author.name].busted = True
                        allBusted = checkAllDone()
                        if allBusted:
                            await ctx.send("everyone is out now")
                            roundNum+=1
                            turnNum = 0
                            await calcPlayerPoints(ctx)
                            win = checkWin()
                            if win:
                                await ctx.send(f"{win} has won!!!!!")
                                return
                            else:
                                await playflipseven(ctx)
                                return
                        deck.pop(0)
                        break
                    else:
                        await ctx.send("saved by the second chance")
                        schance = True
                        players[ctx.author.name].inventory = list(filter(lambda item: item.value != "secondchance", players[ctx.author.name].inventory))
                        deck.pop(0)
                        await playflipseven(ctx)
                        return
                    
            
        if not players[ctx.author.name].busted and not schance:
            card = deck[0]
            players[ctx.author.name].inventory.append(deck.pop(0))
            if card.value == "freeze":
                await ctx.send("enter ?freeze [username of who you want to freeze]")
                return
            if card.value == "flip3":
                await ctx.send("enter ?flip3 [username of who you want to flip 3 cards]")
                return
            allBusted = checkAllDone()
            if allBusted:
                await ctx.send("everyone is out now")
                roundNum+=1
                turnNum = 0
                await calcPlayerPoints(ctx)
                win = checkWin()
                if win:
                    await ctx.send(f"{win} has won!!!!!")
                    return


            gotseven = checkSeven(players[ctx.author.name].inventory)
            if gotseven and not players[ctx.author.name].busted:
                players[ctx.author.name].inventory.append(Card("15", dupebad=True))
                players[ctx.author.name].seven = True
                allDone = checkAllDone()
                if allDone:
                    roundNum+=1
                    turnNum = 0
                    await calcPlayerPoints(ctx)
                    win = checkWin()
                    if win:
                        await ctx.send(f"{win} has won!!!!!")
                        return
                    else:
                        await playflipseven(ctx)
                        return
                    
            inventory_string = ", ".join([card.get_emoji_string(ctx, ctx.bot,card.value) for card in players[ctx.author.name].inventory])
            await ctx.send(f"{ctx.author.name} now has: {inventory_string}")
            turnNum+=1
    else:
        await ctx.send("not you")
        await playflipseven(ctx, notyou=True)
        return
    await playflipseven(ctx)

async def passturn(ctx):
    global turnNum, players, currentPlayer, roundNum
    getCurrentPlayer()
    if ctx.author.name == turnOrder[turnNum % len(turnOrder)]:
        for pid, player in players.items():
            if player.name == turnOrder[turnNum % len(turnOrder)]:
                player.passTurn = True
                currentPlayer = player
        
        turnNum += 1

        inventory_string = ", ".join([card.value for card in currentPlayer.inventory])
        await ctx.send(f"you still have: {inventory_string}")
        allPassed = checkAllDone()
        if allPassed:
            roundNum+=1
            turnNum = 0
            await calcPlayerPoints(ctx)
            win = checkWin()
            if win:
                await ctx.send(f"{win} has won!!!!!")
                return
    else:
        await ctx.send("not you")
        await playflipseven(ctx, notyou=True)
        return
    await playflipseven(ctx)

def getCurrentPlayer():
    global turnNum, turnOrder, currentPlayer, players
    for pid, player in players.items():
        if player.name == turnOrder[turnNum % len(turnOrder)]:
            currentPlayer = player
            return

def checkWin():
    global players
    winning_players = {}
    for pid, player in players.items():
        if player.points > 200:
            winning_players[pid] = player.points
    if len(winning_players) > 0:
        # no ties
        max_points = max(winning_players, key=winning_players.get)
        return max_points
    else:
        return False
    
def checkSeven(inventory):
    dupebadcount = 0
    for card in inventory:
        if card.dupebad:
            dupebadcount += 1
    if dupebadcount == 7:
        return True
    else:
        return False
    
def setupdeck():
    global deck
    deck = []
    deck.append(Card("0", dupebad=True))
    for i in range(13):
        for j in range(i):
            deck.append(Card(str(i), dupebad=True))
    for i in range(5):
        deck.append(Card(str((i+1) * 2), modifier=True))
    for i in range(3):
        deck.append(Card("freeze"))
    deck.append(Card("flip3"))
    deck.append(Card("secondchance"))
    deck.append(Card("timestwo"))


def checkAllDone():
    global players
    allDone = True
    for pid, player in players.items():
        if not player.passTurn and not player.busted and not player.seven:
            allDone = False
            break
    return allDone

def rotateTurnOrder():
    global turnOrder
    d = deque(turnOrder)
    d.rotate(1)
    turnOrder = list(d)

async def freeze(ctx, name):
    global currentPlayer, players
    getCurrentPlayer()
    if ctx.author.name == currentPlayer.name and players[ctx.author.name].inventory[-1].value == "freeze":
        try:
            players[name].passTurn = True
            await ctx.send(f"{name} has been frozen")
            await finish_flip_three(ctx)
        except KeyError:
            await ctx.send("they don't exist")

async def flipthree(ctx, name):
    global deck, players, worstcasescenario
    try:
        players[name]
    except KeyError:
        await ctx.send("they don't exist")
        return
    if players[name].passTurn or players[name].busted or players[name].seven:
        await ctx.send("nuh uh")
        return
    if ctx.author.name == currentPlayer.name and players[ctx.author.name].inventory[-1].value == "flip3":
        worstcaseindex = 4
        for i in range(3):
            schance = False
            if len(deck) == 0:
                    await ctx.send("shuffling...")
                    setupdeck()
                    time.sleep(0.5)
            await ctx.send(f"you drew {deck[0].get_emoji_string(ctx, ctx.bot,deck[0].value)} ({deck[0].value})")
            if deck[0].dupebad:
                for card in players[name].inventory:
                    if card.value == deck[0].value and not card.modifier:
                        if not "secondchance" in [card.value for card in players[ctx.author.name].inventory]:
                            await ctx.send(f"you busted :(")
                            for pid, player in players.items():
                                if player.name == name:
                                    player.busted = True
                                    deck.pop(0)
                                    if worstcasescenario:
                                        players[name].inventory.append(Card("freeze"))
                                    await finish_flip_three(ctx)
                                    return
                        else:
                            await ctx.send("saved by the second chance")
                            players[name].inventory = list(filter(lambda item: item.value != "secondchance", players[name].inventory))
                            deck.pop(0)
                            schance = True
            if not players[name].busted and not schance:
                if deck[0].value == "freeze":
                    await ctx.send("enter ?freeze [username of who you want to freeze] once you have finished")
                    worstcasescenario = True
                    worstcaseindex = i

                if worstcaseindex != i:
                    players[name].inventory.append(deck.pop(0))
                else:
                    deck.pop(0)
                gotseven = checkSeven(players[name].inventory)
                if gotseven and not players[name].busted:
                    players[name].inventory.append(Card("15", dupebad=True))
                    players[name].seven = True
                    if worstcasescenario:
                        players[name].inventory.append(Card("freeze"))
                    await finish_flip_three(ctx)
                    return
                        
                inventory_string = ", ".join([card.get_emoji_string(ctx, ctx.bot,card.value) for card in players[name].inventory])
                await ctx.send(f"{name} now has: {inventory_string}")
        if worstcasescenario:
            players[name].inventory.append(Card("freeze"))
        await finish_flip_three(ctx)
        return

async def finish_flip_three(ctx):
    global players, roundNum, turnNum, worstcasescenario
    if worstcasescenario:
        worstcasescenario = False
        await worstcase(ctx)
        return
    allBusted = checkAllDone()
    if allBusted:
        await ctx.send("everyone is out now")
        roundNum+=1
        turnNum = 0
        await calcPlayerPoints(ctx)
        win = checkWin()
        if win:
            await ctx.send(f"{win} has won!!!!!")
            return
    turnNum += 1
    await playflipseven(ctx)
    return

async def worstcase(ctx):
    await ctx.send("who do you want to freeze?")