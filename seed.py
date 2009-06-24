
## Seeds are used by the spacefilling automaton in map.expandSeeds(). They
# represent a single cell in the automaton.
class Seed:
    def __init__(self, node, life, age):
        ## The "owner" of the seed (a region or TreeNode instance)
        self.node = node
        ## How many ticks before the seed stops expanding
        self.life = life
        ## How many ticks the seed has been alive for
        self.age = age

    def __str__(self):
        return '[Seed: life ' + str(self.life) + '; age ' + str(self.age) + ']'

