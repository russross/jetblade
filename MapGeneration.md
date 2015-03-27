# Introduction #

Map generation is one of the major aspects that makes Jetblade unique. This article describes each step in the process.

# Placing terrain #

Jetblade's maps are broken up into different types of terrain. Each terrain type has a distinct tileset, selection of background objects, and placement and type of tunnels. For example, the "jungle" terrain type has grassy tiles and trees in the background, while the "techpipe" terrain type is more mechanical, and has a rigid, artificial tunnel arrangement. To start out map generation, we need to decide which parts of the working space belong to which terrain. This will dictate how the rest of the generator behaves.

Currently, terrain types have two controls over how they are placed: a desired relative size, and a desired altitude. Neither of these are very exact, but the generator uses them to place "seeds" in a scaled-down version of the map space, which are then expanded (see the spacefilling algorithm section below) to create distinct terrain sectors. We end up with a map that looks something like this:

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/regions.png](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/regions.png)

# Generating the map graph #

Now we need to start deciding where to place tunnels in that layout. Jetblade uses a graph approach to mapmaking (in the mathematical sense of "graph" as a collection of nodes and edges). Each edge corresponds to a single tunnel, and each node is an intersection between tunnels.

First, we want to decide where the player will be able to move from one terrain type to another. Most edges in the graph will not be allowed to cross these boundaries, so the game experience isn't too scattered. We break the map up into chunks of a fixed size, and in each chunk, we examine the local terrain and compare it to the neighboring chunks. If we find a transition point, then we can place a "bridge" edge that crosses the two terrains. We try to place one bridge per terrain pairing, so that each terrain sector is connected to all of its neighbors.

Now we repeat the chunking process, but instead of looking at neighboring chunks, we simply place a node in the chunk. Nodes are placed semi-randomly in normal terrain, or exactly in the center of the chunk for axis-aligned terrain. We also avoid placing nodes near our bridge edges. We end up with a selection of nodes and edges that looks like this:

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/nodes.png](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/nodes.png)

We want to connect all of these nodes together in such a way that no edge is crossing another edge (in math-speak, the graph is "planar"), and the angles between edges are as large as possible. Fortunately, there is a known algorithm to generate graphs like this called the [Delaunay triangulation](http://en.wikipedia.org/wiki/Delaunay_triangulation). It will take our selection of nodes and turn it into this:

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/delaunay.png](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/delaunay.png)

Now we need to reduce that down to just the edges we want to keep. We start out by removing edges that are diagonal in the axis-aligned areas, edges that cross terrain boundaries when they shouldn't, and edges that come too close to other nodes in the graph. That gets us down to this:

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/goodedges.png](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/goodedges.png)

Removing edges like this can get us into trouble, since we could potentially end up removing so many edges that the graph can no longer be connected. This is rather unlikely in practice with maps of a size that people are actually likely to use, but there is a chance of failure here.

Now we want to generate a spanning tree for each terrain sector. Spanning trees are ways to choose edges for a graph such that every node has exactly one path to every other node. Since our spanning trees are restricted to stay inside the terrain sectors, we can use our original bridge edges to connect them together, thus creating this:

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/span.gif](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/span.gif)

And there we have our map graph! We'll be using this to guide the rest of the map generation.

# Carving tunnels #

Now we need to start working with blocks instead of graphs. The game map is composed of a massive array of cells, with each cell either being open space or a block of wall. Our goal is to take the map graph we generated previously and use it to decide where the blocks go and where open space is. To do this, we use a simple cellular automaton that expands to fill space -- the same one we used to create the map regions at the start of this whole process.

We start out by placing "seeds" along the edges of the graph. Each seed is a small object that only knows who its owner is and how long it has to live. The owner is the edge of the graph; the lifespan is determined by how wide we want to make the tunnels in that particular type of terrain.

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/spacefill1.png](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/spacefill1.png)

You can see that we have a few different ways of placing seeds down. The most basic way is to simply place a seed straight along the edge, but there's also a wave pattern and a semi-random distribution. These help vary the shape of the produced tunnels.

Now we're going to step through the automaton. Each step, all of the seeds try to expand outwards, replacing each of their neighboring spaces with copies of themselves that have 1 turn left to live. In the middle of an edge, this works just fine; however, at the junctions and wherever two edges come close to each other, the seeds will encounter other seeds with different owners. When this happens, a wall is created between the two seeds, thus partitioning the map into multiple small rooms, each with no connection to any other room.

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/spacefill2.gif](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/spacefill2.gif)

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/spacefill2.png](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/spacefill2.png)

Now we need to open up the different rooms to their neighbors. Each junction in the map finds each of the nearby walls that are owned by one of the edges that connects to that junction, and converts the wall into open space. That gives us a map that looks like this:

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/junctions.png](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/junctions.png)

The thin walls don't look so good, especially when two unrelated tunnels of differing terrain are near to each other, so we thicken the walls up:

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/thickwalls.png](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/thickwalls.png)

Now we let the different tunnels add their own features. This is intended to allow tunnels to create unique challenges for the player. Currently this is fairly underdeveloped, all we have is a simple jumping puzzle:

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/features.png](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/features.png)

Finally, we need to make certain that the map is accessible to the player. The player can't jump infinitely high, after all. Thus we need to place down platforms that the player can stand on to reach the more inaccessible areas. Of course, we don't want to place platforms if they aren't needed, so the game tries to identify areas that are inaccessible (not just tunnels that can't be reached, but also high ceilings in a single tunnel) by examining the slope and open space in a room.

We use the [Marching Squares](http://en.wikipedia.org/w/index.php?title=Marching_squares&oldid=359601163) algorithm to walk along the walls of each tunnel, checking the local slope. Any time the slope gets too steep, we try to place down platforms. That gets us a map that looks like this:

![http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/platforms.png](http://wiki.jetblade.googlecode.com/hg/images/articles/mapgen/platforms.png)

This part is admittedly not perfect; we still end up with inaccessible tunnels sometimes (for example, in the bright green vertical tunnels in that image) and often get nonsensical platform placements. The basic concept is sound, but it needs some tweaking.

That's it for structural map generation! From here we decide what exact tile each block in the map uses, place down some decorations, and then let the player loose in the newly-created game!