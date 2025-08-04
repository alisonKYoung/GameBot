class Player:
    def __init__(self, PlayerID, Role):
        self.player = PlayerID
        self.role = Role
    def Role(self):
        return(self.role)
    def ID(self):
        return str(self.player)
    def ChangeRole(self, Role):
        self.role = Role