from model import *
import random


class Scene:
    def __init__(self, app, models_data):
        self.app = app
        self.objects = []
        self.load(models_data)


    def add_object(self, obj):
        self.objects.append(obj)

    def load(self, models_data):
        app = self.app
        add = self.add_object
        for data in models_data:
            pos, rot, scale, ppm, mask = data[0], data[1], data[2], data[3], data[4], 
            add(Heart(app, pos, rot, scale, ppm, mask))

    def render(self):
        for obj in self.objects:
            obj.render()

    def animate(self):
        for obj in self.objects:
            obj.animate()
         
