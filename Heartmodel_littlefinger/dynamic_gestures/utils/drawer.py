import cv2

from .enums import Event


class Drawer:
    def __init__(self):
        self.height = self.width = None
        self.action = None
        self.show_delay = 0

    def set_action(self, action):
        """
        Set action to draw

        Parameters
        ----------
        action : Event
            Action to draw
        """
        self.action = action
        self.show_delay = 0

    def draw_two_hands(self, frame, bboxes):
        self.height, self.width, _ = frame.shape
        center_x1, center_y1 = bboxes[0][0] + (bboxes[0][2] - bboxes[0][0]) // 2, bboxes[0][1] + (bboxes[0][3] - bboxes[0][1]) // 2
        center_x2, center_y2 = bboxes[1][0] + (bboxes[1][2] - bboxes[1][0]) // 2, bboxes[1][1] + (bboxes[1][3] - bboxes[1][1]) // 2
        # frame = cv2.circle(frame, (int(center_x1), int(center_y1)), 50, (255, 0, 0), 9)
        # frame = cv2.circle(frame, (int(center_x2), int(center_y2)), 50, (255, 0, 0), 9)

        diff = int(center_x1 - center_x2)

        frame = cv2.rectangle(frame,
                              (int(center_x1), int(center_y1 - diff * 0.3)),
                              (int(center_x2), int(center_y2 + diff * 0.3)),
                              (255, 0, 0), 5)

    def draw(self, frame):
        """
        Draw action on frame

        Parameters
        ----------
        frame : np.ndarray
            Frame to draw on
        x : int
            X coordinate of hand center
        y : int
            Y coordinate of hand center

        Returns
        -------
        frame : np.ndarray
            Frame with action

        """
        if self.height is None:
            self.height, self.width, _ = frame.shape
        if self.action is not None:
            if self.action in [Event.SWIPE_LEFT, Event.SWIPE_LEFT3]:
                frame = cv2.putText(frame, 'SWIPE_LEFT', (self.width // 2, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX ,
                   1, (255, 0, 0) , 5, cv2.LINE_AA)
            elif self.action in [Event.SWIPE_RIGHT, Event.SWIPE_RIGHT3]:
                frame = cv2.putText(frame, 'SWIPE_RIGHT', (self.width // 2, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX ,
                   1, (255, 0, 0) , 5, cv2.LINE_AA)
                   
            elif self.action in [Event.SWIPE_UP, Event.SWIPE_UP3]:
                frame = cv2.putText(frame, 'SWIPE_UP', (self.width // 2, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX ,
                   1, (255, 0, 0) , 5, cv2.LINE_AA)
            elif self.action in [Event.SWIPE_DOWN, Event.SWIPE_DOWN3]:
                frame = cv2.putText(frame, 'SWIPE_DOWN', (self.width // 2, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX ,
                   1, (255, 0, 0) , 5, cv2.LINE_AA)

            elif self.action == Event.ZOOM_OUT:
                frame = cv2.putText(frame, 'ZOOM_OU', (self.width // 2, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX ,
                   1, (255, 0, 0) , 5, cv2.LINE_AA)
            elif self.action == Event.ZOOM_IN:
                frame = cv2.putText(frame, 'ZOOM_IN', (self.width // 2, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX ,
                   1, (255, 0, 0) , 5, cv2.LINE_AA)
                
            elif self.action == Event.DRAG:
                frame = cv2.putText(frame, 'DRAG', (self.width // 2, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX ,
                   1, (255, 0, 0) , 5, cv2.LINE_AA)
            elif self.action == Event.DROP:
                frame = cv2.putText(frame, 'DROP', (self.width // 2, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX ,
                   1, (255, 0, 0) , 5, cv2.LINE_AA)
                   
            elif self.action == Event.DOUBLE_TAP:
                frame = cv2.putText(frame, 'DOUBLE CLICK', (self.width // 2, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX ,  
                   1, (255, 0, 0) , 5, cv2.LINE_AA) 
            elif self.action == Event.TAP:
                frame = cv2.putText(frame, 'CLICK', (self.width // 2, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX ,
                   1, (255, 0, 0) , 5, cv2.LINE_AA)
            
            elif self.action == Event.LITTLE_FINGER:
                frame = cv2.putText(frame, 'LITTLE_FINGER', (self.width // 2, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX ,
                   1, (255, 0, 0) , 5, cv2.LINE_AA)
                   
                   
            self.show_delay += 1
            if self.show_delay > 10:
                self.show_delay = 0
                self.action = None
                self.x = self.y = None

        return frame
