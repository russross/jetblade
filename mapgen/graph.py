import constants
import delaunay
import game
import generator
import edge
import vector2d
from vector2d import Vector2D

import random

## @package mapgraph
# This module is used to generate the graph that underlies the rest of map
# generation. Its makeGraph() function accepts a list of initial edges (in
# the form of Vector2D pairs) that must be in the final graph. These are 
# used to allow the game to know exactly how different regions are connected.
# It returns a list of MapEdge instances, including the seed edges as well
# as others created by the Delaunay triangulation.

## Size of the chunks we break the universe up into for placing nodes.
graphDivisionChunkSize = constants.blockSize * 20
## Minimum distance from the edge of a chunk that a node must be placed. Can't
# exceed half the division chunk size.
minDistanceFromChunkEdge = constants.blockSize * 4
## Minimum distance from any given edge in the graph to a node not in that 
# edge. Edges that are too close get pruned.
minDistanceEdgeToNode = constants.blockSize * 8

## The GraphNode class represents a node in a non-directional planar graph.
class GraphNode(Vector2D):
    ## Instantiate the object
    def __init__(self, first, second = None):
        Vector2D.__init__(self, first, second)
        self.id = constants.globalId
        constants.globalId += 1
        ## Set of adjacent nodes.
        self.neighbors = set()
        ## Local terrain information.
        self.terrain = game.map.getTerrainInfoAtGridLoc(self.toGridspace())
        ## Color of the node, for debugging purposes.
        self.color = [random.randint(64, 255) for i in xrange(3)]


    ## Create a connection to a neighbor node. This only needs to be called
    # for one of the two nodes. Return a new MapEdge representing the link, 
    # or None if we are already connected.
    def addNeighbor(self, neighbor):
        if neighbor not in self.neighbors:
            self.neighbors.add(neighbor)
            neighbor.neighbors.add(self)
            newEdge = edge.MapEdge(self, neighbor)
            return newEdge
        return None


    ## Return true if we are connected to the specified edge or to any of the
    # nodes that the edge connects to (i.e. we are within at least one 
    # degree of separation of either of the edge's nodes).
    def isEdgeRelated(self, edge):
        edgeNodes = set([edge.start, edge.end])
        return self in edgeNodes or edgeNodes.intersection(self.neighbors)


    ## Convert to string.
    def __repr__(self):
        return "[GraphNode at (%s, %s) with %d neighbors]" % (self.x, self.y, len(self.neighbors))



## Generate a set of initial edges that must be in the final map. These
# edges connect the different terrain sectors of the map, and each is 
# axis-aligned.
# \todo Currently this doesn't care that a given terrain type can show up 
# in multiple disconnected chunks in the map.
def getInitialEdges():
    # Helps us track which sectors are already connected.
    terrainMap = dict()
    # Don't use a single node for more than one initial edge, to help space out
    # connections.
    usedNodes = set()
    result = []
    for x, y in getMapChunks():
        start = GraphNode(x + graphDivisionChunkSize / 2,
                          y + graphDivisionChunkSize / 2)
        if start in usedNodes:
            continue
        if start.terrain not in terrainMap:
            terrainMap[start.terrain] = set()
        for offset in vector2d.NEWSPerimeterOrder:
            neighbor = GraphNode(start.add(offset.multiply(graphDivisionChunkSize)))
            if neighbor in usedNodes:
                continue
            if neighbor.terrain not in terrainMap:
                terrainMap[neighbor.terrain] = set()
            if neighbor.terrain not in terrainMap[start.terrain]:
                terrainMap[start.terrain].add(neighbor.terrain)
                terrainMap[neighbor.terrain].add(start.terrain)
                usedNodes.add(start)
                usedNodes.add(neighbor)
                result.append((start, neighbor))
    return result


## Generate a planar graph that covers the map area.
def makeGraph():
    allVerts = set()
    fixedEdges = getInitialEdges()
    for start, end in fixedEdges:
        allVerts.add(start)
        allVerts.add(end)
    # Generate a mapping that tells us where the fixed edges are, so we 
    # can avoid putting nodes near them.
    locToVertMap = dict()
    for vert in allVerts:
        locToVertMap[(int(vert.x / graphDivisionChunkSize), 
                      int(vert.y / graphDivisionChunkSize))] = vert

    # First, generate a random set of verts.
    # Leave a buffer zone of graphDivisionChunkSize around the edges of the 
    # map so we don't have junctions going right up to the edge. This gives
    # our tunnels more room to work.
    for x, y in getMapChunks():
        center = GraphNode(x + graphDivisionChunkSize / 2,
                           y + graphDivisionChunkSize / 2)
        # Ensure that we don't place anything even near to the pre-set edges.
        shouldContinue = True
        centerGrid = center.divide(graphDivisionChunkSize)
        for xOffset in xrange(-1, 2):
            for yOffset in xrange(-1, 2):
                if (centerGrid.ix + xOffset, centerGrid.iy + yOffset) in locToVertMap:
                    shouldContinue = False
                    break
            if not shouldContinue:
                break
        if not shouldContinue:
            continue
        terrain = game.map.getTerrainInfoAtGridLoc(center.toGridspace())
        # If the center of this chunk is in an axis-aligned terrain, then
        # place the new vert in the center.
        if game.map.getRegionInfo(terrain, 'aligned'):
            allVerts.add(center)
        else:
            # Pick a random location a ways away from the edge of the 
            # chunk. 
            loc = GraphNode(
                    random.randint(x + minDistanceFromChunkEdge,
                        x + graphDivisionChunkSize - minDistanceFromChunkEdge),
                    random.randint(y + minDistanceFromChunkEdge,
                        y + graphDivisionChunkSize - minDistanceFromChunkEdge)
            )
            allVerts.add(loc)

    triangulator = delaunay.Triangulator(allVerts, fixedEdges, minDistanceEdgeToNode)
    vertToNeighborsMap = triangulator.makeGraph()
#    triangulator.drawAll(edges = vertToNeighborsMap)
        
    # Convert the mapping of Vector2Ds to sets of Vector2Ds into a list of 
    # MapEdges.
    nodes = {}
    mapEdges = []
    for v1, neighbors in vertToNeighborsMap.iteritems():
        if v1 not in nodes:
            nodes[v1] = GraphNode(v1)
        for v2 in neighbors:
            if v2 not in nodes:
                nodes[v2] = GraphNode(v2)
            newEdge = nodes[v1].addNeighbor(nodes[v2])
            if newEdge:
                mapEdges.append(newEdge)
                
    # Now create dummy edges to connect each node to itself if that node
    # has at least two neighbors, thus creating an object that we can
    # conveniently use to open up the junction areas after the spacefilling
    # automaton (Map.expandSeeds()) has run.
    for node in nodes.values():
        if len(node.neighbors) >= 2:
            newEdge = node.addNeighbor(node)
            if newEdge:
                # \todo How could a node already be attached to itself?
                mapEdges.append(newEdge)

    return mapEdges


## Yield XY pairs every graphDivisionChunkSize, staying one chunk away from
# the edges to give some room to breathe.
def getMapChunks():
    for x in range(graphDivisionChunkSize, 
            game.map.width - graphDivisionChunkSize * 2,
            graphDivisionChunkSize):
        for y in range(graphDivisionChunkSize, 
                game.map.height - graphDivisionChunkSize * 2,
                graphDivisionChunkSize):
            yield x, y
