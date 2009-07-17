
## CollisionData stores the information of a single collision with another
# object.
class CollisionData:
    ## Instantiate a CollisionData
    def __init__(self, vector, distance, type, altObject):
        ## Ejection vector to get out of the other object
        self.vector = vector
        ## Distance to travel along the ejection vector
        self.distance = distance
        ## Descriptor of the collision, e.g. with a solid object, a projectile,
        # etc.
        self.type = type
        ## Object collided with.
        self.altObject = altObject


    ## Return a string representation of the object.
    def __str__(self):
        return ("[Collision of type " + str(self.type) + " against object " + 
                str(self.altObject) + " vector " + str(self.vector) + 
                " distance " + str(self.distance) + "]")
