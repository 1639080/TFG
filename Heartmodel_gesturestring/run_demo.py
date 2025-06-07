
from main import GraphicsEngine #no need to import model or camera, as they are part of the GraphicsEngine
from gesture_action_mapper import GestureActionMapper
import threading

def get_recognized_gesture(gesture_mapper):
    #per simular incoming gesture names
    while True:
        gesture = input("Gesture: ")
        if gesture.lower() == "exit":
            break
        gesture_mapper.handle_gesture(gesture)

def main():
    # first create the app (GraphicsEngine in main.py, that has the camera, scene,...)
    app = GraphicsEngine()
    
    gesture_mapper = GestureActionMapper(
        camera=app.camera,
        model= app.scene.objects[0], #as scene holds a list of 3D objects that includes heartmodel
         graphics_engine=app)

    #run gesture input in a separate thread
    gesture_thread = threading.Thread(target=get_recognized_gesture, args=(gesture_mapper,))
    gesture_thread.start()
    # start the app. render the heart and window
    app.run()

if __name__ == "__main__":
    main()
