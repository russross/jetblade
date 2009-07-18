import prop
import util
from vector2d import Vector2D

import sys

## The PropManager class handles loading prop configuration and selection of
# props depending on terrain.
class PropManager:
    def __init__(self):
        ## Maps prop names to their configuration information.
        # \todo This dict is a huge mess (just check out selectProp()).
        self.propConfigCache = dict()

    ## Choose a prop from the set available for the given terrain, 
    # picking only from props that can be 
    # "planted" on blocks with the given adjacency signature.
    def selectProp(self, terrain, signature):
        if terrain.zone not in self.propConfigCache:
            self.propConfigCache[terrain.zone] = dict()
        if terrain.region not in self.propConfigCache[terrain.zone]:
            # Load the prop config into the config cache first
            filename = 'terrain.' + terrain.zone + '.' + terrain.region + '.props.propConfig'
            module = None
            try:
                module = __import__(filename, globals(), locals(), ['props'])
            except Exception, e:
                util.fatal("Unable to load",filename,":",e.message)
            
            propMap = module.props        
            self.propConfigCache[terrain.zone][terrain.region] = dict()
            self.propConfigCache[terrain.zone][terrain.region]['nameToAnchorMap'] = dict()
            keyToPropWeightsMap = dict()
            for propType, propSettings in propMap.iteritems():
                anchor = Vector2D(propSettings['anchor'])
                # Reverse the anchors to represent the offset we need to add to 
                # properly plant the prop at a given block location
                anchor = anchor.multiply(-1)
                self.propConfigCache[terrain.zone][terrain.region]['nameToAnchorMap'][propType] = anchor
                keys = util.adjacencyArrayToSignatures(propSettings['map'])
                for key in keys:
                    if key not in keyToPropWeightsMap:
                        keyToPropWeightsMap[key] = dict()
                    keyToPropWeightsMap[key][propType] = propSettings['weight']

            self.propConfigCache[terrain.zone][terrain.region]['signatureToWeightsMap'] = keyToPropWeightsMap

        # Select a prop given the adjacency signature for the block it'll be on.
        if signature in self.propConfigCache[terrain.zone][terrain.region]['signatureToWeightsMap']:
            propType = util.pickWeightedOption(self.propConfigCache[terrain.zone][terrain.region]['signatureToWeightsMap'][signature])
            if propType[0] is None or propType[1] is None:
                return None
            anchor = self.propConfigCache[terrain.zone][terrain.region]['nameToAnchorMap'][propType]
            newProp = prop.Prop(anchor, terrain, propType[0], propType[1])
            return newProp
        # No matching prop
        return None


    ## Clear the prop cache.
    def reset(self):
        self.propConfigCache = dict()

