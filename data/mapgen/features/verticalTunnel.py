## @package verticalTunnel This is only invoked from straight.py, which 
# doesn't handle near-vertical
# tunnels well. Simply lay a line of seeds down from the sector's parent to
# its endpoint.
def carveTunnel(map, sector):
    start = sector.parent.loc
    end = sector.loc
    width = sector.getTunnelWidth()
    
    currentLoc = [start[0], start[1]]
    endLoc = [end[0], end[1]]
    if currentLoc[1] > end[1]:
        tmp = currentLoc
        currentLoc = endLoc
        endLoc = tmp

    while currentLoc[1] < endLoc[1]:
        map.plantSeed(currentLoc, sector, width)
        currentLoc[1] += 1

def createFeature(map, sector):
    pass

def shouldCheckAccessibility(sector):
    return True

