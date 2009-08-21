from ...base import terrestrialobject
import game

def getClassName():
    return 'DarkClone'


## Standard "evil clone" of the player.
class DarkClone(terrestrialobject.TerrestrialObject):
    def __init__(self, loc):
        terrestrialobject.TerrestrialObject.__init__(self, loc, game.player.name)
        self.canHang = True
        self.prevVel = self.vel
        self.faction = 'enemy'
        self.health = 40
        self.touchDamage = 10
        ## Id of previous attack that hit us, to prevent attacks from dealing
        # damage more than once.
        # \todo This allows two simultaneous attacks to rapidly deal damage.
        self.prevAttackId = None


    def AIUpdate(self):
        self.runDirection = cmp(0, self.loc.sub(game.player.loc).x)
        if self.state.name == 'hang':
            self.justStartedClimbing = True
        self.prevVel = self.vel


    def processCollision(self, collision):
        terrestrialobject.TerrestrialObject.processCollision(self, collision)
        if (collision.type == 'player' and 
                collision.altObject.touchDamage != 0 and
                collision.altObject.id != self.prevAttackId):
            self.health -= collision.altObject.touchDamage
            self.prevAttackId = collision.altObject.id

