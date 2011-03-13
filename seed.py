
## Seeds are used by the spacefilling automaton in map.expandSeeds(). They
# represent a single cell in the automaton.
class Seed:
    def __init__(self, owner, life, age):
        ## The "owner" of the seed, which lays claim to some portion of the 
        # map area.
        self.owner = owner
        ## How many ticks before the seed stops expanding
        self.life = life
        ## How many ticks the seed has been alive for
        self.age = age

    def __str__(self):
        return '[Seed: life ' + str(self.life) + '; age ' + str(self.age) + ']'

