## @package game This package centralizes access to singletons.

import animationmanager
import configmanager
import dynamicclassmanager
import mapgen.enveffectmanager
import eventmanager
import mapgen.featuremanager
import fontmanager
import mapgen.furnituremanager
import gameobjectmanager
import imagemanager
import mapgen.editor
import mapgen.scenerymanager
import soundmanager

# Load this ahead of time because other modules need it ready so they can
# load their configuration.
dynamicClassManager = dynamicclassmanager.DynamicClassManager()

animationManager = animationmanager.AnimationManager()
configManager = configmanager.ConfigManager()
envEffectManager = mapgen.enveffectmanager.EnvEffectManager()
eventManager = eventmanager.EventManager()
featureManager = mapgen.featuremanager.FeatureManager()
fontManager = fontmanager.FontManager()
furnitureManager = mapgen.furnituremanager.FurnitureManager()
gameObjectManager = gameobjectmanager.GameObjectManager()
imageManager = imagemanager.ImageManager()
mapEditor = mapgen.editor.MapEditor()
sceneryManager = mapgen.scenerymanager.SceneryManager()
soundManager = soundmanager.SoundManager()

