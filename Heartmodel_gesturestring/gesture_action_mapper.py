import pygame as pg
import moderngl as mgl
import sys
from model import Heart
from camera import Camera
from main import GraphicsEngine

class GestureActionMapper:
    def __init__(self, camera:Camera, model: Heart, graphics_engine: GraphicsEngine):
        self.camera = camera #file camera for original camera, zoom in and out
        self.model = model #file model for rotations
        self.graphics_engine = graphics_engine #file main.py, class graphics_engine for perspectives
    
    #handle gestures recognized to functionalities in camera, model, main
    def handle_gesture(self, gesture_name):
        if gesture_name == "click":
            self.camera.reset_position() #camera to original
            self.model.reset_rotation() #rotation to original
        elif gesture_name == "double click":
            self.graphics_engine.toggle_perspective_view() #4 views perspective (file main=graphics engine)
        elif gesture_name == "zoom in":
            self.camera.move_forward() #move camera foward =zoom in (file Camera)
        elif gesture_name == "zoom out":
            self.camera.move_backward() #move camera backward = zoom out (file Camera)
        elif gesture_name == "swipe left":
            self.model.rotate_left() #rotation heart to the left (file model)
        elif gesture_name == "swipe right":
            self.model.rotate_right() #rotation heart to the right (file model)
        elif gesture_name == "swipe up":
            self.model.rotate_up() #rotation heart up (file model)
        elif gesture_name == "swipe down":
            self.model.rotate_down() #rotation heart down (file model)
