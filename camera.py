import jetblade
import util

## The maximum speed for the camera to move, to prevent jerky camera motion 
# if the player teleports.
maxCameraSpeed = 30

## The camera is used to determine the center of the viewscreen. It tracks the 
# player's position.
class Camera:
    ## Instantiate a Camera. 
    def __init__(self):
        ## curLoc and prevLoc are used to interpolate the camera's position for
        # smooth movement between physics updates.
        self.curLoc = list(jetblade.player.getDrawLoc(1))
        self.prevLoc = self.curLoc

    ## Update the camera's current and previous locations. 
    def update(self):
        self.prevLoc = (self.curLoc[0], self.curLoc[1])
        target = jetblade.player.getDrawLoc(1)
        delta = [target[0] - self.curLoc[0], target[1] - self.curLoc[1]]
        magnitude = util.vectorMagnitude(delta)
        if magnitude > maxCameraSpeed:
            delta[0] = delta[0] / magnitude * maxCameraSpeed
            delta[1] = delta[1] / magnitude * maxCameraSpeed
        self.curLoc[0] += delta[0]
        self.curLoc[1] += delta[1]

    ## Interpolate between self.prevLoc and self.curLoc to get the current
    # draw location.
    def getDrawLoc(self, progress):
        # Round the vector off to prevent jitter.
        result = util.roundVector(util.interpolatePoints(self.prevLoc, self.curLoc, progress))
        print "Current camera drawloc is",result,"from",self.prevLoc,self.curLoc,progress
        return result


    def __str__(self):
        return "[Camera at " + str(self.prevLoc) + " moving to " + str(self.curLoc) + "]"

