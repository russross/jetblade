# v.1 #

  * Add a powerup that increases the player's capabilities when collected.
    * Make the map generate a roadblock that requires the powerup to bypass.
  * Add an enemy that hurts the player when they touch. Track player health and end the game when it runs out.
    * Enemy placement should be configured as part of the region data in data/mapgen/zones.py. This file will need to be refactored into a set of region-specific files.
    * Enemy AI should be in a dynamically-loaded module under the data directory.
  * Add attack animations for the player, which hurt enemies if they are hit.
    * Only the attacking part of the player should deal damage; the rest of the player should still be vulnerable to attack.
  * Add an environmental effect that affects physics for creatures that enter it.