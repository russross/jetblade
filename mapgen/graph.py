import constants
import delaunay
import game
import edge
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
class GraphNode:
    ## Instantiate the object
    def __init__(self, loc):
        self.id = constants.globalId
        constants.globalId += 1
        ## Position of this node.
        self.loc = loc
        ## Set of adjacent nodes.
        self.neighbors = set()
        ## Local terrain information.
        self.terrain = game.map.getTerrainInfoAtGridLoc(self.loc.toGridspace())
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
        return "[GraphNode at %s with %d neighbors]" % (self.loc, len(self.neighbors))



## Generate a planar graph, given a list of Vector2D pairs which are the
# fixed edges that we must include.
def makeGraph(seedEdges):
    # First, generate a random set of verts
    allVerts = set([t[0] for t in seedEdges])
    locToVertMap = dict()
    for vert in allVerts:
        locToVertMap[(vert.x / graphDivisionChunkSize, 
                      vert.y / graphDivisionChunkSize)] = vert
    # Leave a buffer zone of graphDivisionChunkSize around the edges of the 
    # map so we don't have junctions going right up to the edge. This gives
    # our tunnels more room to work.
    for x in range(graphDivisionChunkSize, 
            game.map.width - graphDivisionChunkSize * 2,
            graphDivisionChunkSize):
        for y in range(graphDivisionChunkSize, 
                game.map.height - graphDivisionChunkSize * 2,
                graphDivisionChunkSize):
            if (x, y) in locToVertMap:
                continue
            # If the center of this chunk is in an axis-aligned terrain, then
            # place the new vert in the center.
            center = Vector2D(x + graphDivisionChunkSize / 2,
                              y + graphDivisionChunkSize / 2)
            terrain = game.map.getTerrainInfoAtGridLoc(center.toGridspace())
            # The game is not guaranteed to fill the entire map area with
            # terrain markers; ignore failed areas.
            if terrain is None:
                continue
            if game.map.getRegionInfo(terrain, 'aligned'):
                allVerts.add(center)
            else:
                # Pick a random location a ways away from the edge of the 
                # chunk. 
                loc = Vector2D(
                        random.randint(x + minDistanceFromChunkEdge,
                            x + graphDivisionChunkSize - minDistanceFromChunkEdge),
                        random.randint(y + minDistanceFromChunkEdge,
                            y + graphDivisionChunkSize - minDistanceFromChunkEdge)
                )
                allVerts.add(loc)
    
    triangulator = delaunay.Triangulator(allVerts, minDistanceEdgeToNode)
    vertToNeighborsMap = triangulator.makeGraph()
#    triangulator.drawAll(edges = vertToNeighborsMap)
    for v1, v2 in seedEdges:
        vertToNeighborsMap[v1].add(v2)
        vertToNeighborsMap[v2].add(v1)
        
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



