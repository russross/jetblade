import prop
import util

import sys

## The PropManager class handles loading prop configuration and selection of
# props depending on terrain.
class PropManager:
    def __init__(self):
        ## Maps prop names to their configuration information.
        self.propConfigCache = dict()

    ## Choose a prop from the set available for the given region (as 
    # determined by terrain and flavor), picking only from props that can be 
    # "planted" on blocks with the given adjacency signature.
    def selectProp(self, terrain, flavor, signature):
        if terrain not in self.propConfigCache:
            self.propConfigCache[terrain] = dict()
        if flavor not in self.propConfigCache[terrain]:
            # Load the prop config into the config cache first
            filename = 'terrain.' + terrain + '.' + flavor + '.props.propconfig'
            module = None
            try:
                module = __import__(filename, globals(), locals(), ['props'])
            except Exception, e:
                print "Unable to load",filename,":",e.message
                return None
            
            propMap = module.props        
            self.propConfigCache[terrain][flavor] = dict()
            self.propConfigCache[terrain][flavor]['nameToAnchorMap'] = dict()
            keyToPropWeightsMap = dict()
            for propType, propSettings in propMap.iteritems():
                anchor = propSettings['anchor']
                # Reverse the anchors to represent the offset we need to add to 
                # properly plant the prop at a given block location
                anchor = (-anchor[0], -anchor[1])
                self.propConfigCache[terrain][flavor]['nameToAnchorMap'][propType] = anchor
                keys = util.adjacencyArrayToSignatures(propSettings['map'])
                for key in keys:
                    if key not in keyToPropWeightsMap:
                        keyToPropWeightsMap[key] = dict()
                    keyToPropWeightsMap[key][propType] = propSettings['weight']

            self.propConfigCache[terrain][flavor]['signatureToWeightsMap'] = keyToPropWeightsMap

        # Select a prop given the adjacency signature for the block it'll be on.
        if signature in self.propConfigCache[terrain][flavor]['signatureToWeightsMap']:
            propType = util.pickWeightedOption(self.propConfigCache[terrain][flavor]['signatureToWeightsMap'][signature])
            if propType[0] is None or propType[1] is None:
                return None
            anchor = self.propConfigCache[terrain][flavor]['nameToAnchorMap'][propType]
            newProp = prop.Prop(anchor, terrain, flavor, propType[0], propType[1])
            return newProp
        # No matching prop
        return None


    ## Clear the prop cache.
    def reset(self):
        self.propConfigCache = dict()

