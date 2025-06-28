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
        
        if gesture_name == "LITTLE_FINGER": #reset global
            self.camera.reset_position() #camera to original
            self.model.reset_rotation() #rotation to original
            self.graphics_engine.reset_heartbeat() #heartbeat animation to normal
            #reiniciar musica de fons SI s'ha parat. no vull reiniciar tota l'estona
            try:
                if not pg.mixer.music.get_busy():
                    pg.mixer.music.load("Eerie_Carlota.mp3")
                    pg.mixer.music.set_volume(0.05)
                    pg.mixer.music.play(-1)
                    print("🔄 Background music reset")
            except Exception as e:
                print(f"[Warning] Could not reset music: {e}")
                
        elif gesture_name == "TAP":
            #4 views perspective (file main=graphics engine)
            self.graphics_engine.toggle_perspective_view()
        elif gesture_name == "ZOOM_IN":
            #move camera foward =zoom in (file Camera)
            self.camera.move_forward()
        elif gesture_name == "ZOOM_OUT":
            #move camera backward = zoom out (file Camera)
            self.camera.move_backward()
        elif gesture_name == "SWIPE_LEFT":
            #rotation heart to the left (file model)
            self.model.rotate_left()
        elif gesture_name == "SWIPE_RIGHT":
            #rotation heart to the right (file model)
            self.model.rotate_right()
        elif gesture_name == "SWIPE_UP":
            #rotation heart up (file model)
            self.model.rotate_up()
        elif gesture_name == "SWIPE_DOWN":
            #rotation heart down (file model)
            self.model.rotate_down()
        elif gesture_name == "DRAG":
            #min heartbeat (file main)
            self.graphics_engine.set_min_heartbeat()
        elif gesture_name == "DROP":
            #max heartbeat (file main)
            self.graphics_engine.set_max_heartbeat()
        elif gesture_name == "STOP":
            #parar el heartbeat animation i musica.
            self.graphics_engine.stop_heartbeat() #file main.
            try:
                pg.mixer.music.stop()
                print("background music stopped")
            except Exception as e:
                print("Could not stop music: {e}")
        
        
