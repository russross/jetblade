#!/usr/local/bin/python2.5
import pyximport; pyximport.install()
from vector2d import Vector2D
import line
from line import Line

NUMNODES = 15
NODESPACING = 33
SHOULD_DRAW = True
SHOULD_SAVE = False

import cProfile
import math
import random
import sys

if len(sys.argv) > 1:
    random.seed(sys.argv[1])

import pygame
import pygame.locals
pygame.init()
screen = pygame.display.set_mode((800, 600))


## Sort vertices by their distance to the given vertex.
def sortByDistanceTo(location):
    return lambda a, b: int(a.distanceSquared(location) - b.distanceSquared(location))

## Sort vectors into a consistent, if arbitrary, order.
def sortVectors(a, b):
    return (a.ix - b.ix) * 1000000 + (a.iy - b.iy)


## Class for generating Delaunay triangulations of graphs.
class Triangulator:
    def __init__(self):
        ## List of all nodes in the graph
        self.nodes = []
        for x in range(0, 800 - NODESPACING, NODESPACING * 2):
            for y in range(0, 600 - NODESPACING, NODESPACING * 2):
                if x >= 300 and x <= 500 and y >= 100 and y <= 500:
                    # Lock the location to the grid
                    self.nodes.append(
                            Vector2D(x + NODESPACING / 2, y + NODESPACING / 2))
                else:
                    self.nodes.append(
                            Vector2D(random.randint(x, x + NODESPACING), 
                                     random.randint(y, y + NODESPACING)))

        ## Maps node to list of nodes it is connected to.
        self.edges = dict()
        ## For drawing coordinates
        self.font = pygame.font.Font("data/fonts/MODENINE.TTF", 12)
        ## Number of times we've drawn, for saving output
        self.drawCount = 0


    ## Generate a triangulation of our nodes
    def triangulate(self):
        print "Generating a triangulation from",len(self.nodes),"nodes"
        # 1. Pick seed node.
        seed = random.choice(self.nodes)
        # nodeSet is the set of nodes not currently in the triangulation.
        nodeSet = set(self.nodes)
        nodeSet.remove(seed)
        exteriorNodes = list(nodeSet)

        # 2. Sort by distance to seed node.
        exteriorNodes.sort(sortByDistanceTo(seed))

        # 3. Find node closest to seed node.
        closestNode = exteriorNodes[0]
        nodeSet.remove(closestNode)

        # 4. Find node that creates smallest circumcircle. Equation for a 
        # circumcircle's coordinates can be found at 
        # http://en.wikipedia.org/wiki/Circumcircle#Coordinates_of_circumcenter
        # Treat calculations as if seed were at the center
        bPrime = closestNode.sub(seed)
        smallestRadius = None
        bestNode = None
        bestCenter = None
        for node in nodeSet:
            cPrime = node.sub(seed)
            # \todo d is 0 in rare situations.
            d = 2 * (bPrime.x * cPrime.y - bPrime.y - cPrime.x)
            centerX = (cPrime.y * (bPrime.x ** 2 + bPrime.y ** 2) - \
                       bPrime.y * (cPrime.x ** 2 + cPrime.y ** 2)) / d
            centerY = (bPrime.x * (cPrime.x ** 2 + cPrime.y ** 2) - \
                       cPrime.x * (bPrime.x ** 2 + bPrime.y ** 2)) / d
            center = Vector2D(centerX, centerY).add(seed)
            radius = center.sub(seed).magnitudeSquared()
            if smallestRadius is None or radius < smallestRadius:
                smallestRadius = radius
                bestNode = node
                bestCenter = center
        nodeSet.remove(bestNode)

        # 5. Force order to be right-handed; form starting convex hull.
        hull = [seed, closestNode, bestNode]
        a = closestNode.sub(seed)
        b = bestNode.sub(seed)
        direction = cmp(a.x * b.y - a.y * b.x, 0)
        if direction < 0:
            hull = [seed, bestNode, closestNode]

        # Construct edge mapping.
        for i in xrange(3):
            self.edges[hull[i]] = set([hull[(i - 1) % 3], hull[(i + 1) % 3]])

        # List of all nodes contained by the hull.
        interiorNodes = list(hull)

        self.drawAll(self.nodes, interiorNodes)

        # 6. Resort remaining nodes by distance to the center of the 
        # circumcircle; this is the order we will add the nodes to the 
        # triangulation.
        exteriorNodes = list(nodeSet)
        exteriorNodes.sort(sortByDistanceTo(bestCenter))

        # 7. Expand convex hull to encompass each new node in turn, adding 
        # triangles to all visible nodes.
        while exteriorNodes:
            node = exteriorNodes.pop(0)
            # hull is now a list of nodes in the convex hull of the
            # triangulation thus far. Prune out occluded edges.
            visibleEdges = []
            # Track how many times we are able to see each node: should be 
            # 2 for nodes that are made interior by the new node, 1 for 
            # nodes that are connected to the new node but still exterior, and
            # 0 otherwise.
            nodeSeenCount = dict([(n, 0) for n in hull])
            for edge in [(n, hull[(i + 1) % len(hull)]) for i, n in enumerate(hull)]:
                a = edge[0].sub(node)
                b = edge[1].sub(edge[0])
                direction = cmp(a.x * b.y - a.y * b.x, 0)
                if direction < 0: 
                    visibleEdges.append(edge)
                    nodeSeenCount[edge[0]] += 1
                    nodeSeenCount[edge[1]] += 1
            self.edges[node] = set()
            for a, b in visibleEdges:
                # Connect the new node to all visible exterior nodes.
                self.edges[a].add(node)
                self.edges[b].add(node)
                self.edges[node].add(a)
                self.edges[node].add(b)
            # Insert the new node into the hull. We have two cases here: 
            # * Some nodes are rendered interior by the new node. In that case,
            #   we remove those edges from the hull, and insert the new node
            #   where they were.
            # * No nodes were rendered interior by the new node. That means that
            #   the new node connects only to two old nodes, and should go
            #   between them in the hull.
            if len(visibleEdges) > 1:
                # Find nodes that show up twice in visibleEdges; those nodes are
                # no longer in the hull.
                newHull = []
                newNodeIndex = None
                for i, n in enumerate(hull):
                    if nodeSeenCount[n] < 2:
                        newHull.append(n)
                    else:
                        newNodeIndex = len(newHull)
                newHull.insert(newNodeIndex, node)
                hull = newHull
            else:
                newHull = list(hull)
                # Find the two visible nodes in the hull, insert new node 
                # between them.
                for i, n in enumerate(hull):
                    j = (i + 1) % len(hull)
                    n2 = hull[j]
                    if (n, n2) in visibleEdges:
                        newHull.insert(j, node)
                        break
                hull = newHull

            interiorNodes.append(node)
            self.drawAll(self.nodes, interiorNodes)

        self.drawAll(self.nodes, interiorNodes, shouldForceSave = True)


    ## Given that we're done making a triangulation, make that triangulation
    # into a Delaunay triangulation by flipping the shared edge of any two
    # adjacent triangles that are not Delaunay.
    # ( http://en.wikipedia.org/wiki/Delaunay_triangulation#Visual_Delaunay_definition:_Flipping )
    def makeDelaunay(self):
        # These are the edges that we know will never need to be flipped, as
        # they are on the perimeter of the graph.
        hull = self.constructHullFrom(Vector2D(-1, -1), self.nodes)
        sortedHull = set()
        for i, vertex in enumerate(hull):
            # Ensure vertices are in a consistent ordering so we can do 
            # lookups on the hull later.
            tmp = [vertex, hull[(i + 1) % len(hull)]]
            tmp.sort(sortVectors)
            sortedHull.add(tuple(tmp))

        # Queue is technically a misnomer here, since it implies order but
        # this is unordered (as it doesn't need to be ordered).
        edgeQueue = set()
        # Add all non-exterior edges to the edge queue.
        for sourceNode, targetNodes in self.edges.iteritems():
            for targetNode in targetNodes:
                tmp = [sourceNode, targetNode]
                tmp.sort(sortVectors)
                tmp = tuple(tmp)
                if tmp not in sortedHull and tmp not in edgeQueue:
                    # Edge is interior edge.
                    edgeQueue.add(tmp)

        while edgeQueue:
            (v1, v2) = edgeQueue.pop()
            n1, n2 = self.getNearestNeighbors(v1, v2)

            if not self.isDelaunay(v1, v2, n1, n2):
                # Triangles are not Delaunay; flip them.
                if v2 in self.edges[v1]:
                    self.edges[v1].remove(v2)
                if v1 in self.edges[v2]:
                    self.edges[v2].remove(v1)
                self.edges[n1].add(n2)
                self.edges[n2].add(n1)
                for vertPair in [(v1, n1), (v1, n2), (v2, n1), (v2, n2)]:
                    tmp = list(vertPair)
                    tmp.sort(sortVectors)
                    tmp = tuple(tmp)
                    if tmp not in sortedHull and tmp not in edgeQueue:
                        edgeQueue.add(tmp)
                self.drawAll(edges = self.edges, dirtyEdges = edgeQueue)
        self.drawAll(edges = self.edges, shouldForceSave = True)
  

    ## Find the two triangles that share the specified edge, by sorting
    # neighbors by how far they are from the edge, and getting the two on
    # either side of the edge (i.e. closest positive and negative
    # distances).
    def getNearestNeighbors(self, v1, v2):
        neighborCandidates = []
        for neighbor in self.edges[v1]:
            if neighbor in self.edges[v2]:
                neighborCandidates.append(neighbor)
        perpendicular = v2.sub(v1).invert()
        positives = []
        negatives = []
        for neighbor in neighborCandidates:
            distance = neighbor.dot(perpendicular) - perpendicular.dot(v1)
            if distance < 0:
                negatives.append((neighbor, distance))
            else:
                positives.append((neighbor, distance))
        if not negatives or not positives:
            return None, None
        negatives.sort(lambda a, b: int(b[1] - a[1]))
        positives.sort(lambda a, b: int(a[1] - b[1]))
        return negatives[0][0], positives[0][0]


    # Calculate the angles (v1, n1, v2) and (v1, n2, v2) and return True iff
    # their sum is less than pi.
    def isDelaunay(self, v1, v2, n1, n2):
        angleSum = 0
        for i, vertex in enumerate([n1, n2]):
            a1 = v1.sub(vertex).angle()
            a2 = v2.sub(vertex).angle()
            if a1 < 0:
                a1 += 2 * math.pi
            if a2 < 0:
                a2 += 2 * math.pi
            if i == 0:
                angle = a1 - a2
            else:
                angle = a2 - a1
            if angle < 0:
                angle += 2 * math.pi
            angleSum += angle
        return angleSum < math.pi

   
    ## Return true if an edge from node1 to node2 crosses any of the given edges
    def crossesEdge(self, node1, node2):
        newLine = Line(node1, node2)
        for source, targets in self.edges.iteritems():
            for target in targets:
                altLine = Line(source, target)
                collision = newLine.lineLineIntersect(altLine)
                if collision == line.LINE_INTERSECT:
                    return True
        return False


    # Construct the convex hull of interiorNodes by way of an exterior location.
    def constructHullFrom(self, node, interiorNodes):
        # Find closest node in the given list of nodes that can be reached 
        # without crossing an existing edge.
        interiorNodes.sort(sortByDistanceTo(node))
        closestIndex = 0
        while self.crossesEdge(node, interiorNodes[closestIndex]):
            closestIndex += 1
        closest = interiorNodes[closestIndex]
        hullNodes = []
        curNode = closest
        prevNode = node
        while curNode not in hullNodes:
            # Walk around the perimeter of the set of nodes, by finding the 
            # neighbor node whose angle is most clockwise from our last
            # angle.
            hullNodes.append(curNode)
            angle = prevNode.sub(curNode).angle()
            if angle < 0:
                angle += 2 * math.pi
            neighbors = self.edges[curNode]
            bestDistance = None
            bestNode = None
            for neighbor in neighbors:
                if neighbor == prevNode:
                    continue
                neighborAngle = neighbor.sub(curNode).angle()
                if neighborAngle < 0:
                    neighborAngle += 2 * math.pi
                clockwiseDistance = angle - neighborAngle
                # Force all distances to be in the same range so 
                # comparisons work.
                while clockwiseDistance > 2 * math.pi:
                    clockwiseDistance -= 2 * math.pi
                while clockwiseDistance < 0:
                    clockwiseDistance += 2 * math.pi
                if bestNode is None or clockwiseDistance < bestDistance:
                    bestDistance = clockwiseDistance
                    bestNode = neighbor
            prevNode = curNode
            curNode = bestNode
        while curNode != hullNodes[0]:
            # Started our trace of the hull from inside; therefore, remove 
            # occluded nodes.
            # \todo Does this ever actually happen?
            hullNodes.pop(0)
        return hullNodes


    def drawNodes(self, color, shouldLabelNodes, *args):
        for node in args:
            pygame.draw.circle(screen, color, (node.ix, 600 - node.iy), 2)
            if shouldLabelNodes:
                label = self.font.render("%d,%d" % (node.ix, node.iy), True, (255, 255, 255))
                rect = label.get_rect()
                rect.left = node.ix + 5
                rect.top = 600 - node.iy + 5
                screen.blit(label, rect)


    def drawAll(self, allNodes = None, interiorNodes = [], edges = None, 
                dirtyEdges = [], shouldForceSave = False, 
                shouldLabelNodes = False):
        if not SHOULD_DRAW:
            return
        if edges is None:
            edges = self.edges
        screen.fill((0, 0, 0), None)
        if allNodes is not None:
            self.drawNodes((255, 0, 0), shouldLabelNodes, *allNodes)
        self.drawNodes((0, 255, 0), shouldLabelNodes, *interiorNodes)
        for node, connections in edges.iteritems():
            for connection in connections:
                if (node, connection) not in dirtyEdges and (connection, node) not in dirtyEdges:
                    pygame.draw.line(screen, (255, 255, 255), 
                            (node.ix, 600 - node.iy),
                            (connection.ix, 600 - connection.iy))
        for node1, node2 in dirtyEdges:
            pygame.draw.line(screen, (255, 0, 0), (node1.ix, 600 - node1.iy),
                    (node2.ix, 600 - node2.iy))

        if SHOULD_SAVE or shouldForceSave:
            self.drawCount += 1
            pygame.image.save(screen, "graph%04d.png" % self.drawCount)
            print "Saved status update",self.drawCount
        pygame.display.update()


def run():
    triangulator = Triangulator()
    triangulator.triangulate()
    triangulator.makeDelaunay()

cProfile.run('run()', 'profiling.txt')
