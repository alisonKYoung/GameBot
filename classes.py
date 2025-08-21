class Game:
    def __init__(self, ctx, playerIds):
        self.channelContext = ctx
        self.playerIds = playerIds
    def createPlayers(self, PlayerClass):
        self.players = {}
        for i in self.playerIds:
            self.players[i.name] = PlayerClass(i.id, i.name, i.display_name)
            self.playerNames = list(self.players.keys())

class Player:
    def __init__(self, playerId, name, nickname):
        self.playerId = playerId
        self.name = name
        self.nickname = nickname