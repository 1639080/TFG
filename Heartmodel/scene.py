from model import *
import random

#Defines the scene class which manages and renders 3D objects == the Heart is the first.
class Scene:
    def __init__(self, app, models_data):
        self.app = app
        self.objects = [] #all objects in scene
        self.load(models_data) #load initial objects

    #add a single object
    def add_object(self, obj):
        self.objects.append(obj)
    
    #load objects from models_data: app, pos, rot, scale, ppm, mask
    def load(self, models_data):
        app = self.app
        add = self.add_object
        for data in models_data:
            pos, rot, scale, ppm, mask = data[0], data[1], data[2], data[3], data[4], 
            add(Heart(app, pos, rot, scale, ppm, mask))
    
    #render objects
    def render(self):
        for obj in self.objects:
            obj.render()
    
    #animate objects
    def animate(self):
        for obj in self.objects:
            obj.animate()
         
