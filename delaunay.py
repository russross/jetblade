#!/usr/local/bin/python2.5
import pyximport; pyximport.install()
from vector2d import Vector2D
import line
from line import Line

INFINISLOPE = 10 ** 6
LINELEN = 1000
NUMNODES = 15
NODESPACING = 50
SHOULD_DRAW = True

import math
import random
import sys

if len(sys.argv) > 1:
    random.seed(sys.argv[1])

import pygame
import pygame.locals
pygame.init()
screen = pygame.display.set_mode((800, 600))


def sortByDistanceTo(location):
    return lambda a, b: int(a.distanceSquared(location) - b.distanceSquared(location))

def sortVectors(a, b):
    return (a.ix - b.ix) * 1000000 + (a.iy - b.iy)

## Return true if an edge from node1 to node2 crosses any of the given edges
def crossesEdge(node1, node2, edges):
    newLine = Line(node1, node2)
    for source, targets in edges.iteritems():
        for target in targets:
            altLine = Line(source, target)
            collision = newLine.lineLineIntersect(altLine)
            if collision == line.LINE_INTERSECT:
                return True
    return False

# Construct the convex hull of interiorNodes by way of an exterior location.
def constructHullFrom(node, interiorNodes):
    # Find closest node that's already in the triangulation.
    interiorNodes.sort(sortByDistanceTo(node))
    closestIndex = 0
    while crossesEdge(node, interiorNodes[closestIndex], edges):
        closestIndex += 1
    closest = interiorNodes[closestIndex]
#    print "Closest interior node is",closest
    hullNodes = []
    curNode = closest
    prevNode = node
    while curNode not in hullNodes:
        hullNodes.append(curNode)
        angle = prevNode.sub(curNode).angle()
        if angle < 0:
            angle += 2 * math.pi
        neighbors = edges[curNode]
#        print "Checking neighbors",[str(i) for i in neighbors],"against angle",angle
        bestDistance = None
        bestNode = None
        for neighbor in neighbors:
            if neighbor == prevNode:
                continue
            neighborAngle = neighbor.sub(curNode).angle()
            if neighborAngle < 0:
                neighborAngle += 2 * math.pi
            clockwiseDistance = angle - neighborAngle
            # Force all distances to be in the same range so comparisons work.
            while clockwiseDistance > 2 * math.pi:
                clockwiseDistance -= 2 * math.pi
            while clockwiseDistance < 0:
                clockwiseDistance += 2 * math.pi
#            print "Neighbor",neighbor,"has angle",neighborAngle,"with clockwise distance",clockwiseDistance,"compare best",bestDistance
            if bestNode is None or clockwiseDistance < bestDistance:
                bestDistance = clockwiseDistance
                bestNode = neighbor
        prevNode = curNode
        curNode = bestNode
#        print "Traveling to next node",curNode
    while curNode != hullNodes[0]:
#        print "Removing node",hullNodes[0],"from hull"
        # Started our trace of the hull from inside; therefore, remove 
        # occluded nodes.
        hullNodes.pop(0)
    return hullNodes


font = pygame.font.Font("data/fonts/MODENINE.TTF", 12)
def drawNodes(color, *args):
    for node in args:
        pygame.draw.circle(screen, color, (node.ix, 600 - node.iy), 2)
#        label = font.render("%d,%d" % (node.ix, node.iy), True, (255, 255, 255))
#        rect = label.get_rect()
#        rect.left = node.ix + 5
#        rect.top = 600 - node.iy + 5
#        screen.blit(label, rect)


count = 0
interiorNodes = []
edges = {}
def drawAll(allNodes = None, interiorNodes = interiorNodes, edges = edges, 
            dirtyEdges = []):
    if not SHOULD_DRAW:
        return
    global count
    count += 1
    print "Drawing graph #%d" % count
    screen.fill((0, 0, 0), None)
    if allNodes is not None:
        drawNodes((255, 0, 0), *allNodes)
    drawNodes((0, 255, 0), *interiorNodes)
    for node, connections in edges.iteritems():
        for connection in connections:
            if (node, connection) not in dirtyEdges and (connection, node) not in dirtyEdges:
                pygame.draw.line(screen, (255, 255, 255), 
                        (node.ix, 600 - node.iy),
                        (connection.ix, 600 - connection.iy))
    for node1, node2 in dirtyEdges:
        pygame.draw.line(screen, (255, 0, 0), (node1.ix, 600 - node1.iy),
                (node2.ix, 600 - node2.iy))


    if len(sys.argv) == 3:
        pygame.image.save(screen, "graph%04d.png" % count)
    pygame.display.update()

nodes = []
curX = 0
curY = 0
# Generate a set of randomly-placed nodes.
#for i in xrange(NUMNODES):
#    curX += random.randint(200, 800)
#    curY += random.randint(200, 600)
#    while curX > 800:
#        curX -= 800
#    while curY > 600:
#        curY -= 600
#    nodes.append(Vector2D(curX, curY))
# Generate a set of nodes placed randomly within notional grid cells.
for x in range(0, 800, NODESPACING * 2):
    for y in range(0, 600, NODESPACING * 2):
        nodes.append(Vector2D(random.randint(x, x + NODESPACING), 
                              random.randint(y, y + NODESPACING)))

# Fixed set of nodes.
#for x, y in [(300, 350), (300, 500), (180, 400),  (400, 400), (225, 325)]:
#    nodes.append(Vector2D(x, y))

print "Generating triangulation for",len(nodes),"nodes"

drawAll(allNodes = nodes, edges = {})

# 1. Pick seed node.
seed = random.choice(nodes)
seed = nodes[3]
nodeSet = set(nodes)
nodeSet.remove(seed)
nodes = list(nodeSet)

# 2. Sort by distance to seed node.
nodes.sort(sortByDistanceTo(seed))

# 3. Find node closest to seed node.
closestNode = nodes[0]
nodeSet.remove(closestNode)

# 4. Find node that creates smallest circumcircle
center1 = seed.average(closestNode)
slope1 = seed.sub(closestNode).slope()
inverseSlope1 = INFINISLOPE
if abs(slope1) > .0001:
    inverseSlope1 = -1.0 / slope1
offset = Vector2D(1, inverseSlope1).multiply(LINELEN)
line1 = Line(center1.sub(offset), center1.add(offset))
smallestRadius = None
bestNode = None
bestIntersect = None
for node in nodes[1:]:
    center2 = node.average(closestNode)
    slope2 = node.sub(closestNode).slope()
    inverseSlope2 = INFINISLOPE
    if abs(slope2) > .0001:
        inverseSlope2 = -1.0 / slope2
    offset = Vector2D(1, inverseSlope2).multiply(LINELEN)
    line2 = Line(center2.sub(offset), center2.add(offset))
    intersect = line2.infiniteLineIntersect(line1)
    while intersect == line.LINE_PARALLEL:
        # HACK: this indicates that the lines are parallel, i.e. were made
        # from collinear nodes. Jitter one of the nodes.
        node = node.addX(random.choice([-1, 1])).addY(random.choice([-1, 1]))
        # \todo Remove the code duplication here.
        center2 = node.average(closestNode)
        slope2 = node.sub(closestNode).slope()
        inverseSlope2 = INFINISLOPE
        if abs(slope2) > .0001:
            inverseSlope2 = -1.0 / slope2
        offset = Vector2D(1, inverseSlope2).multiply(LINELEN)
        line2 = Line(center2.sub(offset), center2.add(offset))
        intersect = line2.infiniteLineIntersect(line1)

    radius = intersect.sub(seed).magnitudeSquared()
    if smallestRadius is None or radius < smallestRadius:
        smallestRadius = radius
        bestNode = node
        bestIntersect = intersect
nodeSet.remove(bestNode)

# 5. Force order to be right-handed; form starting convex hull.
hull = [seed, closestNode, bestNode]
a = closestNode.sub(seed)
b = bestNode.sub(seed)
direction = cmp(a.x * b.y - a.y * b.x, 0)
if direction < 0:
    hull = [seed, bestNode, closestNode]

# Construct edge mapping.
edges = dict()
for i in xrange(3):
    edges[hull[i]] = set([hull[(i - 1) % 3], hull[(i + 1) % 3]])

# List of all nodes contained by the hull.
interiorNodes = list(hull)
#print "Starting nodes are",[str(i) for i in interiorNodes]

drawAll(nodes, interiorNodes, edges)

# 6. Resort remaining nodes by distance to the center of the circumcircle.
nodes = list(nodeSet)
nodes.sort(sortByDistanceTo(bestIntersect))

# 7. Expand convex hull to encompass each new node in turn, adding triangles
# to all visible nodes.
while nodes:
    node = nodes.pop(0)
#    print "\nChecking node",node
    hullNodes = constructHullFrom(node, interiorNodes)
#    print "Generated convex hull",[str(i) for i in hullNodes]
    # hullNodes is now a list of nodes in the convex hull of the triangulation
    # thus far. Prune out occluded edges.
    visibleEdges = []
    for n1, n2 in [(n, hullNodes[(i + 1) % len(hullNodes)]) for i, n in enumerate(hullNodes)]:
        a = n1.sub(node)
        b = n2.sub(n1)
        direction = cmp(a.x * b.y - a.y * b.x, 0)
#        print "Direction of edge",node,n1,n2,"is",direction
        if direction > 0: 
            visibleEdges.append((n1, n2))
#    print "Visible edges are",[(str(a),str(b)) for a,b in visibleEdges]
#    print "Added node",node,"to triangulation"
    edges[node] = set()
    for a, b in visibleEdges:
        edges[a].add(node)
        edges[b].add(node)
        edges[node].add(a)
        edges[node].add(b)
    interiorNodes.append(node)
    drawAll(nodes, interiorNodes, edges)

drawAll(nodes, interiorNodes, edges)
# 8. Find pairs of triangles that do not meet the Delaunay condition 
# ( http://en.wikipedia.org/wiki/Delaunay_triangulation#Visual_Delaunay_definition:_Flipping )
# and flip them.
edgeQueue = []
hull = constructHullFrom(Vector2D(-1, -1), interiorNodes)
sortedHull = []
for i, vertex in enumerate(hull):
    tmp = [vertex, hull[(i + 1) % len(hull)]]
    tmp.sort(sortVectors)
    sortedHull.append(tuple(tmp))

print "\n"

for sourceNode, targetNodes in edges.iteritems():
    for targetNode in targetNodes:
        tmp = [sourceNode, targetNode]
        tmp.sort(sortVectors)
        tmp = tuple(tmp)
        if tmp not in sortedHull and tmp not in edgeQueue:
            # Edge is interior edge.
            edgeQueue.append(tmp)

markedEdges = set()

while edgeQueue:
    (v1, v2) = edgeQueue.pop(0)
    if (v1, v2) in sortedHull:
        continue
    print "Checking edge",v1,v2,"for flipping"
    markedEdges.add((v1, v2))
    # Find the two triangles that share this edge.
    neighborCandidates = []
    for neighbor in edges[v1]:
        if neighbor in edges[v2]:
            neighborCandidates.append(neighbor)
    # Sort neighbors by how far they are from the edge, and get the two on
    # either side of the edge (i.e. closest positive and negative distances)
    projectionLine = Line(v1, v2)
    neighborCandidates = [(v, projectionLine.pointDistance(v)) for v in neighborCandidates]
    for i in xrange(len(neighborCandidates)):
        # Flip sign for neighbors on the other side of the edge.
        neighbor, distance = neighborCandidates[i]
        a = v1.sub(v2)
        b = v2.sub(neighbor)
        direction = cmp(a.x * b.y - a.y * b.x, 0)
        if direction > 0: 
            distance *= -1
        neighborCandidates[i] = (neighbor, distance)
            
    neighborCandidates.sort(lambda a, b: int(a[1] - b[1]))
    leastNegative = None
    leastPositive = None
    for neighbor in neighborCandidates:
        if neighbor[1] > 0:
            if leastPositive is None or neighbor[1] < leastPositive[1]:
                leastPositive = neighbor
        else:
            if leastNegative is None or neighbor[1] > leastNegative[1]:
                leastNegative = neighbor
    if leastNegative is None or leastPositive is None:
        continue
    n1, n2 = leastPositive[0], leastNegative[0]
    print "Edge",v1,v2,"shared with",n1,n2
    
    # Calculate the angles with the shared verts.
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
        print "From",vertex,"got subangles",a1,a2,"for result",angle
        angleSum += angle
    print "Angle total is",angleSum
    
    if angleSum > math.pi:
        # Triangles are not Delaunay; flip them.
        print "Flipping"
        if v2 in edges[v1]:
            edges[v1].remove(v2)
        if v1 in edges[v2]:
            edges[v2].remove(v1)
        edges[n1].add(n2)
        edges[n2].add(n1)
        for vertPair in [(v1, n1), (v1, n2), (v2, n1), (v2, n2)]:
            tmp = list(vertPair)
            tmp.sort(sortVectors)
            tmp = tuple(tmp)
            if tmp in markedEdges:
                markedEdges.remove(tmp)
            if tmp not in sortedHull:
                edgeQueue.append(tmp)
        drawAll(edges = edges, dirtyEdges = edgeQueue)
    else:
        # Triangles are already Delaunay.
        print "No flip needed"



