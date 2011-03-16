## @package game This package centralizes access to singletons.

import animationmanager
import configmanager
import dynamicclassmanager
import enveffectmanager
import eventmanager
import featuremanager
import fontmanager
import furnituremanager
import gameobjectmanager
import imagemanager
import mapgen.editor
import scenerymanager
import soundmanager

# Load this ahead of time because other modules need it ready so they can
# load their configuration.
dynamicClassManager = dynamicclassmanager.DynamicClassManager()
animationManager = animationmanager.AnimationManager()
configManager = configmanager.ConfigManager()
envEffectManager = enveffectmanager.EnvEffectManager()
eventManager = eventmanager.EventManager()
featureManager = featuremanager.FeatureManager()
fontManager = fontmanager.FontManager()
furnitureManager = furnituremanager.FurnitureManager()
gameObjectManager = gameobjectmanager.GameObjectManager()
imageManager = imagemanager.ImageManager()
mapEditor = mapgen.editor.MapEditor()
sceneryManager = scenerymanager.SceneryManager()
soundManager = soundmanager.SoundManager()

