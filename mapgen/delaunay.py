import constants
import game
import line
import logger
import quadtree
from vector2d import Vector2D

import math
import os
import pygame
import random
import sys

## @package mapgen.delaunay
# This module contains the code that generates the edges in the graph that
# forms the basis for map generation. The Triangulator class is here, along
# with several constants.

## Minimum angular distance between two neighbors in the graph.
MIN_ANGLE_DISTANCE = math.pi / 3

## Number of times to try generating a spanning tree that hits every node 
# in a subset of the graph
NUM_SPANNING_ATTEMPTS = 1000

## Minimum distance between two nodes (in terms of number of edge hops) before
# we consider trying to place a shortcut between them.
MIN_SHORTCUT_HOPS = 6


## Sort vertices by their distance to the given vertex.
def sortByDistanceTo(location):
    return lambda a, b: int(a.distanceSquared(location) - b.distanceSquared(location))


## Sort vectors into a consistent, if arbitrary, order.
def sortVectors(a, b):
    return cmp(a.ix, b.ix) or cmp(a.iy, b.iy)


## Simple wrapper class for Vector2D instances that allows them to be 
# added to quadtrees.
class VectorWrap():
    def __init__(self, vector):
        self.vector = vector
    def getBounds(self):
        return pygame.rect.Rect(self.vector.x, self.vector.y, 
                self.vector.x + constants.EPSILON, 
                self.vector.y + constants.EPSILON)


## Class for generating Delaunay triangulations of graphs.
class Triangulator:
    def __init__(self, nodes, fixedEdges, minDistanceEdgeToNode):
        ## List of all nodes in the graph, as GraphNodes
        self.nodes = list(nodes)

        ## Set of GraphNode pairs representing edges that must be in the 
        # final graph.
        self.fixedEdges = fixedEdges
    
        # Figure out the min/max extent of the nodes
        minX = minY = maxX = maxY = None
        for node in nodes:
            if minX is None:
                minX = maxX = node.x
                minY = maxY = node.y
            minX = min(minX, node.x)
            maxX = max(maxX, node.x)
            minY = min(minY, node.y)
            maxY = max(maxY, node.y)
        self.min = Vector2D(minX - 1, minY - 1)
        self.max = Vector2D(maxX + 1, maxY + 1)

        # Make a tree to hold the nodes so we can quickly look up which
        # nodes are near a given edge.
        rect = pygame.rect.Rect(self.min.x, self.min.y, self.max.x, self.max.y)
        self.nodeTree = quadtree.QuadTree(rect)
        self.nodeTree.addObjects([VectorWrap(v) for v in self.nodes])

        ## Maps node to list of nodes it is connected to.
        self.edges = dict()
        ## Minimum distance between an edge and any node not in that edge.
        # Violators will be pruned.
        self.minDistanceEdgeToNode = minDistanceEdgeToNode
        ## Number of times we've drawn, for saving output
        self.drawCount = 0
        ## A font for output; strictly for debugging purposes.
        self.font = pygame.font.Font(os.path.join(constants.fontPath, 'MODENINE.TTF'), 14)


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
            d = 2 * (bPrime.x * cPrime.y - bPrime.y * cPrime.x)
            if d == 0:
                # Three nodes are collinear; there's no such thing as an 
                # inscribed circumcircle in this case.
                continue
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
#            self.drawAll(self.nodes, interiorNodes)

#        self.drawAll(self.nodes, interiorNodes, shouldForceSave = True)


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
#                self.drawAll(edges = self.edges, dirtyEdges = edgeQueue)
#        self.drawAll(edges = self.edges, shouldForceSave = True)
        totalEdges = 0
        for node, targetNodes in self.edges.iteritems():
            totalEdges += len(targetNodes)
        totalEdges /= 2
        print "Final triangulation has",totalEdges,"edges"


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
        newLine = line.Line(node1, node2)
        for source, targets in self.edges.iteritems():
            for target in targets:
                altLine = line.Line(source, target)
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


    ## Remove undesirable edges. These are edges that come too close to 
    # other nodes, and edges that cross terrain boundaries. Any edges in
    # self.fixedEdges are by definition desirable, so they always stay.
    # high degree of interconnectedness between nodes, this should never
    # cause the graph to become disconnected, but really we have no guarantee.
    def removeBadEdges(self):
#        self.drawAll()
        newEdges = dict()
        for node, neighbors in self.edges.iteritems():
            newEdges[node] = set()
            for neighbor in neighbors:
                edge = line.Line(node, neighbor)
                edgeRect = edge.getBounds()
                edgeRect.left -= self.minDistanceEdgeToNode
                edgeRect.top -= self.minDistanceEdgeToNode
                edgeRect.width += 2 * self.minDistanceEdgeToNode
                edgeRect.height += 2 * self.minDistanceEdgeToNode
                isSafeEdge = True
                # No edges connecting different regions of the map.
                if node.terrain != neighbor.terrain:
                    isSafeEdge = False
                # No non-axis-aligned edges in axis-aligned parts of the map.
                elif (game.map.getRegionInfo(node.terrain, 'aligned') and
                        game.map.getRegionInfo(neighbor.terrain, 'aligned') and
                        abs(node.x - neighbor.x) > constants.EPSILON and
                        abs(node.y - neighbor.y) > constants.EPSILON):
                    isSafeEdge = False
                else:
                    for vecWrap in self.nodeTree.getObjectsIntersectingRect(edgeRect):
                        nearNode = vecWrap.vector
                        if (nearNode not in [node, neighbor] and 
                                edge.pointDistance(nearNode) < self.minDistanceEdgeToNode):
                            isSafeEdge = False
                            break
                if isSafeEdge:
                    newEdges[node].add(neighbor)

        self.edges = self.addFixedEdges(newEdges)
#        self.drawAll()
#        self.drawAll(shouldForceSave = True)


    ## Modify the given map of nodes to sets of nodes so that it includes
    # our fixed edges.
    def addFixedEdges(self, newEdges):
        for v1, v2 in self.fixedEdges:
            if v1 not in newEdges:
                newEdges[v1] = set()
            if v2 not in newEdges:
                newEdges[v2] = set()
            newEdges[v1].add(v2)
            newEdges[v2].add(v1)
        return newEdges


    ## Decide which edges in the triangulation will actually be used for 
    # the final map. We generate a spanning tree for each individual terrain
    # group; these are then connected using our fixed edges.
    def span(self):
#        self.drawAll()
        # First determine which nodes are in which connected groups.
        groups = []
        seenNodes = set()
        for node in self.nodes:
            if node not in seenNodes:
                # Find all connected nodes
                queue = [node]
                newGroup = set()
                while queue:
                    curNode = queue.pop()
                    seenNodes.add(curNode)
                    newGroup.add(curNode)
                    for neighbor in self.edges[curNode]:
                        if neighbor.terrain == curNode.terrain and neighbor not in seenNodes:
                            queue.append(neighbor)
                groups.append(newGroup)

        newEdges = dict([(node, set()) for node in self.edges.keys()])
        seenNodes = set()
        for group in groups:
            # Generate a spanning tree limited to this group.
            groupEdges = self.makeSpanningTree(group)
            # Now try to add some loops within it.
            groupEdges = self.addLoopbacks(groupEdges)
            newEdges.update(groupEdges)
#            self.drawAll(edges = newEdges)
        return self.addFixedEdges(newEdges)


    ## Generate a spanning tree that is limited to nodes in the specified
    # group. Because of our limitations on minimum angle between edges,
    # this is not guaranteed to hit every edge in the group, so we retry 
    # some number of times.
    def makeSpanningTree(self, nodeGroup):
        for i in xrange(NUM_SPANNING_ATTEMPTS):
            # Pick a random starting node in the group.
            modGroup = set(nodeGroup)
            newEdges = dict([(node, set()) for node in list(nodeGroup)])
            temp = list(modGroup)
            random.shuffle(temp)
            start = temp[0]
            seenNodes = set([start])

            # Use None to mark the end of tree expansion at a given depth.
            queue = [start, None]
            while queue:
                node = queue.pop(0)
                if node is None:
                    if not queue:
                        # Out of nodes to add to the spanning tree!
                        break
                    # Finished connecting to all the nodes at this depth.
                    # Shuffle this set of nodes, to break up patterns that would
                    # otherwise emerge in the less random node layouts, and to
                    # give us a chance of finding a working arrangement in
                    # more unusual patterns.
                    random.shuffle(queue)
                    queue.append(None)
                    continue
                modGroup.remove(node)
                for neighbor in self.edges[node]:
                    if neighbor not in seenNodes and neighbor in nodeGroup:
                        # Make certain that adding the neighbor would not create
                        # too acute an angle with any existing edges.
                        neighborVector = neighbor.sub(node)
                        canAddEdge = True
                        for alt in newEdges[node]:
                            altVector = alt.sub(node)
                            angleDistance = altVector.angleWithVector(neighborVector)
                            if abs(angleDistance) < MIN_ANGLE_DISTANCE:
                                canAddEdge = False
                        if canAddEdge:
                            seenNodes.add(neighbor)
                            newEdges[node].add(neighbor)
                            newEdges[neighbor].add(node)
                            queue.append(neighbor)
#                self.drawAll(interiorNodes = list(seenNodes), 
#                        edges = newEdges, allNodes = list(nodeGroup))
#        self.drawAll(edges = newEdges, shouldForceSave = True)
            if not modGroup:
                # Every node was added to the spanning tree, so we're good
                # to go!
                return newEdges
        self.drawAll(interiorNodes = list(nodeGroup), 
                edges = dict([(node, self.edges[node]) for node in nodeGroup]), 
                allNodes = list(nodeGroup), shouldLabelNodes = True)
        logger.fatal("Unable to make a spanning tree that hit every edge in %s" % nodeGroup)
        return None


    ## Given a selection of edges, look for good places to insert loops. A 
    # good place is one that creates a shortcut between two nodes that 
    # previously were far apart. 
    def addLoopbacks(self, edges):
        if len(edges) == 1:
            return edges
        result = dict(edges)
        while True:
            # Maps each node pair to the distance between the two nodes.
            nodePairToDistanceMap = self.dijkstra(result)
            
            # Find the node pair that we could connect with a single edge
            # that are furthest away from each other in the current graph.
            maxDistance = -1
            worstNodes = None
            for node in edges.keys():
                for neighbor in self.edges[node]:
                    pair = (node, neighbor)
                    if (pair in nodePairToDistanceMap and 
                            nodePairToDistanceMap[pair] > maxDistance and
                            self.isEdgeLegal(pair, result)):
                        maxDistance = nodePairToDistanceMap[pair]
                        worstNodes = pair
                        
            if maxDistance < MIN_SHORTCUT_HOPS or worstNodes is None:
                # Either not worth adding an edge, or we found no valid
                # edge to add.
                break

            result[worstNodes[0]].add(worstNodes[1])
            result[worstNodes[1]].add(worstNodes[0])
#            self.drawAll(edges = result)

        return result


    ## Calculate the distance from each node to each other node, using
    # Dijkstra's algorithm. Return a mapping of tuples to the distances 
    # between them. 
    # \todo Is this really the most efficient way to get these values? And
    # all we really care about is the two nodes with the longest path length
    # between them, but unfortunately that's an NP-complete problem and is
    # of course entirely unsolvable for cyclic graphs.
    def dijkstra(self, edges):
        nodePairToDistanceMap = {}
        nodes = set(edges.keys())
        for node in nodes:
            # Maps each node to the shortest distance to that node.
            distanceMap = dict([(n, constants.BIGNUM) for n in nodes])
            distanceMap[node] = 0
            firstNode = list(edges[node])[0]
            distanceMap[firstNode] = 1
            isFirst = True
            queue = list(nodes.difference(set([firstNode])))
            while queue:
                if isFirst:
                    closestNode = firstNode
                    isFirst = False
                else:
                    closestNode = queue.pop(0)
                for neighbor in edges[closestNode]:
                    pathDistance = distanceMap[closestNode] + 1
                    if pathDistance < distanceMap[neighbor]:
                        distanceMap[neighbor] = pathDistance
                queue.sort(lambda a, b: cmp(distanceMap[a], distanceMap[b]))
            for altNode, distance in distanceMap.iteritems():
                nodePairToDistanceMap[(node, altNode)] = distance
        return nodePairToDistanceMap


    ## Return true if the edge does not form too sharp an angle with the 
    # existing edges and does not come too close to any other nodes.
    def isEdgeLegal(self, nodePair, edges):
        orders = [(nodePair[0], nodePair[1]), (nodePair[1], nodePair[0])]
        for n1, n2 in orders:
            vector = n1.sub(n2)
            for alt in edges[n1]:
                if alt not in nodePair:
                    altVector = n1.sub(alt)
                    angleDistance = altVector.angleWithVector(vector)
                    if abs(angleDistance) < MIN_ANGLE_DISTANCE:
                        return False

        edgeLine = line.Line(nodePair[0], nodePair[1])
        edgeRect = edgeLine.getBounds()
        for vecWrap in self.nodeTree.getObjectsIntersectingRect(edgeRect):
            nearNode = vecWrap.vector
            if (nearNode not in nodePair and 
                    edgeLine.pointDistance(nearNode) < self.minDistanceEdgeToNode):
                return False
        return True


    ## Run the entire process, starting from raw nodes and ending with a 
    # minimum spanning tree of a Delaunay triangulation of those nodes.
    def makeGraph(self):
        self.drawAll(dirtyEdges = self.fixedEdges, allNodes = self.nodes)
        self.triangulate()
#        self.drawAll(edges = self.edges)
        self.makeDelaunay()
#        self.drawAll(edges = self.edges)
        self.removeBadEdges()
#        self.drawAll(edges = self.edges)
        result = self.span()
        self.drawAll(edges = result, dirtyEdges = self.fixedEdges)
        return result


    ## Draw the nodes in the graph. Purely for debugging purposes.
    def drawNodes(self, outputImage, color, shouldLabelNodes, *args):
        for node in args:
            drawX = int(node.ix * 800 / self.max.x)
            drawY = int(node.iy * 800 / self.max.y)
            pygame.draw.circle(outputImage, color, (drawX, drawY), 2)
            if shouldLabelNodes:
                label = self.font.render("%d,%d" % (node.ix, node.iy), True, (255, 255, 255))
                rect = label.get_rect()
                rect.left = drawX + 5
                rect.top = drawY + 5
                outputImage.blit(label, rect)


    ## Draw the graph and save it to a file. This is strictly for debugging
    # purposes.
    # Note that while the edges parameter is a dict mapping nodes to sets
    # of nodes, the dirtyEdges parameter is a list of node-node pairs.
    def drawAll(self, allNodes = None, interiorNodes = [], edges = None, 
                dirtyEdges = [], shouldForceSave = False, 
                shouldLabelNodes = False):
        outputImage = pygame.Surface((800, 800))
        if edges is None:
            edges = self.edges
        outputImage.fill((0, 0, 0), None)
        if allNodes is not None:
            self.drawNodes(outputImage, (255, 0, 0), shouldLabelNodes, *allNodes)
        self.drawNodes(outputImage, (0, 255, 0), shouldLabelNodes, *interiorNodes)

        for node, connections in edges.iteritems():
            aX = node.ix * 800 / self.max.x
            aY = node.iy * 800 / self.max.y
            for connection in connections:
                bX = connection.ix * 800 / self.max.x
                bY = connection.iy * 800 / self.max.y
                if (node, connection) not in dirtyEdges and (connection, node) not in dirtyEdges:
                    pygame.draw.line(outputImage, (255, 255, 255), 
                            (aX, aY), (bX, bY))
        for node1, node2 in dirtyEdges:
            aX = node1.ix * 800 / self.max.x
            aY = node1.iy * 800 / self.max.y
            bX = node2.ix * 800 / self.max.x
            bY = node2.iy * 800 / self.max.y
            pygame.draw.line(outputImage, (255, 0, 0), (aX, aY), (bX, bY))

        self.drawCount += 1
        pygame.image.save(outputImage, "graph%04d.png" % self.drawCount)
        print "Saved status update",self.drawCount


