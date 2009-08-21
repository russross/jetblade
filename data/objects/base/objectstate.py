

## The ObjectState class encapsulates logic specific to a given game object's
# current state (e.g. running, jumping, crawling, attacking, etc.). All of the
# major functions specified for PhysicsObject are specified for ObjectState
# with the idea that subsidiaries of PhysicsObject should passthrough to 
# ObjectState for the bulk of their logic.
class ObjectState:
    def __init__(self, owner):
        self.owner = owner


    def AIUpdate(self):
        pass


    def preCollisionUpdate(self):
        pass


    def postCollisionUpdate(self):
        pass


    def adjustCollision(self, collision):
        return collision


    def hitTerrain(self, collision):
        return True


    def hitWall(self, collision):
        return True


    def hitCeiling(self, collision):
        return True


    def hitFloor(self, collision):
        return True


    def completeAnimation(self, animation):
        return self.owner.loc

