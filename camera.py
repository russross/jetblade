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
        self.curLoc = jetblade.player.getDrawLoc(1).copy()
        self.prevLoc = self.curLoc

    ## Update the camera's current and previous locations. 
    def update(self):
        self.prevLoc = self.curLoc.copy()
        target = jetblade.player.getDrawLoc(1)
        delta = target.sub(self.curLoc)
        magnitude = delta.magnitude()
        if magnitude > maxCameraSpeed:
            delta = delta.multiply(maxCameraSpeed / magnitude)
        self.curLoc = self.curLoc.add(delta)

    ## Interpolate between self.prevLoc and self.curLoc to get the current
    # draw location.
    def getDrawLoc(self, progress):
        # Round the vector off to prevent jitter.
        return self.prevLoc.interpolate(self.curLoc, progress)


    def __str__(self):
        return "[Camera at " + str(self.prevLoc) + " moving to " + str(self.curLoc) + "]"

