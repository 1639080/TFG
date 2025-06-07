import argparse
import time
import threading
import cv2
import numpy as np
import cv2

from dynamic_gestures.main_controller import MainController
from dynamic_gestures.utils.drawer import Drawer
from dynamic_gestures.utils import Event

from main import GraphicsEngine #no need to import model or camera, as they are part of the GraphicsEngine
from gesture_action_mapper import GestureActionMapper


def gesture_loop(args, gesture_mapper):
    #init gesture system
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    #initialized the gesture detection system
    controller = MainController(args.detector, args.classifier)
    drawer = Drawer()
    debug_mode = args.debug

    while cap.isOpened():
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        if not ret:
            break

        start_time = time.time()
        #bounding boxes for detected gestures, unique IDs for tracked hands and gesture labels
        bboxes, ids, labels = controller(frame)

        if debug_mode:
            if bboxes is not None:
                bboxes = bboxes.astype(np.int32)
                for i, box in enumerate(bboxes):
                    gesture_name = str(labels[i]) if labels[i] is not None else "None"
                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (255, 255, 0), 4)
                    cv2.putText(frame, f"ID {ids[i]} : {gesture_name}", (box[0], box[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            fps = 1.0 / (time.time() - start_time)
            cv2.putText(frame, f"fps {fps:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if len(controller.tracks) > 0:
            count_of_zoom = 0
            thumb_boxes = []

            for trk in controller.tracks:
                if trk["tracker"].time_since_update < 1 and len(trk["hands"]):
                    hand = trk["hands"][-1]

                    if trk["hands"].action is not None:
                        action = trk["hands"].action

                        if action in [Event.SWIPE_LEFT, Event.SWIPE_LEFT3]:
                            gesture_mapper.handle_gesture("SWIPE_LEFT")
                            print("Gesture detected: SWIPE_LEFT")
                        elif action in [Event.SWIPE_RIGHT, Event.SWIPE_RIGHT3]:
                            gesture_mapper.handle_gesture("SWIPE_RIGHT")
                            print("Gesture detected: SWIPE_RIGHT")
                        elif action in [Event.SWIPE_UP, Event.SWIPE_UP3]:
                            gesture_mapper.handle_gesture("SWIPE_UP")
                            print("Gesture detected: SWIPE_UP")
                        elif action in [Event.SWIPE_DOWN, Event.SWIPE_DOWN3]:
                            gesture_mapper.handle_gesture("SWIPE_DOWN")
                            print("Gesture detected: SWIPE_DOWN")
                        elif action == Event.ZOOM_IN:
                            gesture_mapper.handle_gesture("ZOOM_IN")
                            print("Gesture detected: ZOOM_IN")
                        elif action == Event.ZOOM_OUT:
                            gesture_mapper.handle_gesture("ZOOM_OUT")
                            print("Gesture detected: ZOOM_OUT")
                        elif action in [Event.TAP, Event.DOUBLE_TAP]:
                            gesture_mapper.handle_gesture("TAP")
                            print("Gesture detected: TAP")
                        elif action == Event.LITTLE_FINGER:
                            gesture_mapper.handle_gesture("LITTLE_FINGER")
                            print("Gesture detected: LITTLE_FINGER")

                        trk["hands"].action = None

                    if hand.gesture == 3: #Assuming this is a zoom-hand state
                        count_of_zoom += 1
                        thumb_boxes.append(hand.bbox)

            if count_of_zoom == 2:
                drawer.draw_two_hands(frame, thumb_boxes)

        if debug_mode:
            frame = drawer.draw(frame)
            gesture_mapper.graphics_engine.update_camera_frame(frame)


        #cv2.imshow("Dynamic Gesture Detection", frame) 
        if cv2.waitKey(1) & 0xFF == ord("c"):
            break

    cap.release()
    cv2.destroyAllWindows()


def run(args):
    # # Start HeartModel rendering engine
    ## first create the app (GraphicsEngine in main.py, that has the camera, scene,...)
    app = GraphicsEngine()
    #a bridge between gestures and action on the 3Dmodel
    gesture_mapper = GestureActionMapper(
        camera=app.camera,
        model=app.scene.objects[0], #as scene holds a list of 3D objects that includes heartmodel. first object in scene=Heart
        graphics_engine=app #control rendering
    )

    # Run gesture system in background thread. 
    gesture_thread = threading.Thread(target=gesture_loop, args=(args, gesture_mapper), daemon=True)
    gesture_thread.start()

    # Run heart rendering in main thread
    app.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run gesture-controlled heart model demo")

    parser.add_argument("--detector", default="dynamic_gestures/models/hand_detector.onnx", type=str)
    parser.add_argument("--classifier", default="dynamic_gestures/models/crops_classifier.onnx", type=str)
    parser.add_argument("--debug", required=False, action="store_true", help="Enable debug drawing")

    args = parser.parse_args()
    run(args)

