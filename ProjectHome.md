Jetblade is a 2D platforming game in the style of the Metroid and Castlevania series,
with procedurally-generated maps. At the moment it is still deep in
development, and while you can make interesting maps and explore them with the player avatar, there is no real goal to gameplay yet. Jetblade is an open-source
project, and your contributions are welcome!

Jetblade is written in Python with PyGame. It uses Cython for some modules for speed.

Broadly, the project can be broken down into the following categories:
  * Large-scale procedural map generation, the creation of a selection of tunnels and their interconnections, the selection of different types of regions, the ensuring of general accessibility, and the creation of specific roadblocks to add meaning to exploration.
  * Small-scale procedural map generation, the definition of what a region of the map is like, and the creation of interesting features at the scale of an individual tunnel or room.
  * Platforming gameplay, the implementation of 2D physics in a run&jump context, the addition of abilities to the player, and the creation of new creatures for the player to encounter and possibly battle.

[Download the project](http://code.google.com/p/jetblade/wiki/GettingStarted) and check it out! Or head over to the [project blog](http://jetbladeproject.blogspot.com/) to see the latest developments!

![http://wiki.jetblade.googlecode.com/hg/images/maps/thumbs/samplemap4.png](http://wiki.jetblade.googlecode.com/hg/images/maps/thumbs/samplemap4.png)