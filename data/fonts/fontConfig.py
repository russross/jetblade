## @package fontConfig This package allows you to configure fonts. At the 
# moment this is pretty basic. Fonts must be located in data/fonts and must
# have an entry in this file to be used in-game. Available knobs to configure:
#  * lineHeightMultiplier: represents how tall a line is in comparison to the 
#    size of the font in points. E.g. with a multiplier of .5, a size-6 font
#    would have a line height of 3 pixels. 
#  * sizes: List of font sizes to load at the start of the program. You don't
#    have to provide this -- fonts will be loaded during the game if a
#    not-yet-loaded size is called for -- but it could cause a blip of slowdown.
fonts = {
    'ETHNOCEN': {
        'lineHeightMultiplier': .85,
    },
    'MODENINE': {
        'lineHeightMultiplier': .85,
    },
}
