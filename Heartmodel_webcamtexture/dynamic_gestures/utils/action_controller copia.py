from scipy.spatial import distance #calculate distance between points
from collections import deque

from .enums import Event, HandPosition, targets
from .hand import Hand

#custom sliding buffer that stores a short history of recent hands (hand objects) and checks: if the hand moved in a certain way, if the hand held a gesture for enough frames, if gesture -> motion transitions match known patterns
class Deque:
    def __init__(self, maxlen=30, min_frames=20):
        self.maxlen = maxlen #how many hands to keep in history (last 30 frames)
        self._deque = []
        self.action = None #the current action this gesture represents
        self.min_absolute_distance = 1.5
        self.min_frames = min_frames #minimum duration to consider a gesture real, 20 frames
        self.action_deque = deque(maxlen=5) #short buffer (5) to track repeated events like taps

    def __len__(self):
        return len(self._deque)

    def index_position(self, x):
        for i in range(len(self._deque)):
            if self._deque[i].position == x:
                return i

    def index_gesture(self, x):
        for i in range(len(self._deque)):
            if self._deque[i].gesture == x:
                return i

    def __getitem__(self, index):
        return self._deque[index]

    def __setitem__(self, index, value):
        self._deque[index] = value

    def __delitem__(self, index):
        del self._deque[index]

    def __iter__(self):
        return iter(self._deque)

    def __reversed__(self):
        return reversed(self._deque)
    
    #called every frame with a new Hand object. Converts its gesture to a motion label (Hand position)
    #triggers gesture detection logic via check_is_action(x) = where gestures are recognized
    def append(self, x):
        if self.maxlen is not None and len(self) >= self.maxlen:
            self._deque.pop(0)
        self.set_hand_position(x)
        self._deque.append(x)
        self.check_is_action(x)
    
    #check duration, validate gesture quality
    def check_duration(self, start_index, min_frames=None):
        """
        Check duration of swipe.
        start_index : int #Index of start position of swipe.

        Returns:bool #True if duration of swipe is more than min_frames.
        """
        if min_frames == None:
            min_frames = self.min_frames
        if len(self) - start_index >= min_frames:
            return True
        else:
            return False
        
    def check_duration_max(self, start_index, max_frames=10):
        """
        Check duration of swipe.
        start_index : int #Index of start position of swipe.

        Returns: bool #True if duration of swipe is more than min_frames.
        """
        if len(self) - start_index <= max_frames:
            return True
        else:
            return False
    
    @staticmethod
    def check_horizontal_swipe(start_hand, x):
        """
        Check if swipe is horizontal.

        start_hand : Hand #Hand object of start position of swipe.

        x : Hand #Hand object of end position of swipe.

        Returns: bool #True if swipe is horizontal.
        """
        boundary = [start_hand.bbox[1], start_hand.bbox[3]]
        if boundary[0] < x.center[1] < boundary[1]:
            return True
        else:
            return False

    @staticmethod
    def check_vertical_swipe(start_hand, x):
        """
        Check if swipe is vertical.

        start_hand : Hand #Hand object of start position of swipe.
        x : Hand #Hand object of end position of swipe.

        Returns: bool #True if swipe is vertical.
        """
        boundary = [start_hand.bbox[0], start_hand.bbox[2]]
        if boundary[0] < x.center[0] < boundary[1]:
            return True
        else:
            return False
    
    def swipe_distance(self, first_hand: Hand, last_hand: Hand):
        """
        Check if swipe distance is more than min_distance.

        first_hand : Hand #Hand object of start position of swipe.
        last_hand : Hand #Hand object of end position of swipe.

        Returns: bool #True if swipe distance is more than min_distance.

        """
        hand_dist = distance.euclidean(first_hand.center, last_hand.center)
        hand_size = (first_hand.size + last_hand.size) / 2
        return hand_dist / hand_size > self.min_absolute_distance

    def __contains__(self, item):
        for x in self._deque:
            if x.position == item:
                return True

    def set_hand_position(self, hand: Hand):
        """
        Set hand position.
        
        hand : Hand #Hand object.
        """
        #SWIPE UP AND SWIPE DOWN
        #palm-like gestures. If already hand down- this must be end of and upward
        #otherwise, start of upward motion
        if hand.gesture in [31, 35, 36]: # [palm, stop, stop_inv]
            if HandPosition.DOWN_START in self:
                hand.position = HandPosition.UP_END #swipe up
            else:
                hand.position = HandPosition.UP_START
        elif hand.gesture == 0: # hand_down
            if HandPosition.UP_START in self:
                hand.position = HandPosition.DOWN_END
            else:
                hand.position = HandPosition.DOWN_START

        
        #SWIPE RIGHT AND SWIPE LEFT:
        elif hand.gesture == 1: # hand_right
            if HandPosition.LEFT_START in self:
                hand.position = HandPosition.RIGHT_END
            else:
                hand.position = HandPosition.RIGHT_START
        elif hand.gesture == 2: # hand_left
            if HandPosition.RIGHT_START in self:
                hand.position = HandPosition.LEFT_END
            else:
                hand.position = HandPosition.LEFT_START
        
        
        #FAST_SWIPE_UP and FAST_SWIPE_DOWN
        elif hand.gesture == 30: # one
            if HandPosition.FAST_SWIPE_UP_START in self:
                hand.position = HandPosition.FAST_SWIPE_UP_END
            else:
                hand.position = HandPosition.FAST_SWIPE_DOWN_START
        elif hand.gesture == 19: # point
            if HandPosition.FAST_SWIPE_DOWN_START in self:
                hand.position = HandPosition.FAST_SWIPE_DOWN_END
            else:
                hand.position = HandPosition.FAST_SWIPE_UP_START

        #DRAG
        elif hand.gesture == 17: # grabbing
            hand.position = HandPosition.DRAG_START
        
        
        #ZOOM OUT AND ZOOM IN
        elif hand.gesture == 25: # fist
            if HandPosition.ZOOM_OUT_START in self:
                hand.position = HandPosition.ZOOM_OUT_END
            else:
                hand.position = HandPosition.ZOOM_IN_START
        elif hand.gesture == 3: # thumb_index
            if HandPosition.ZOOM_IN_START in self:
                hand.position = HandPosition.ZOOM_IN_END
            else:
                hand.position = HandPosition.ZOOM_OUT_START
        elif hand.gesture == 38: # three2
            if HandPosition.ZOOM_IN_START in self:
                hand.position = HandPosition.ZOOM_IN_END
            else:
                hand.position = HandPosition.ZOOM_OUT_START


        #SWIPE_RIGHT2 and SWIPE_LEFT2
        elif hand.gesture == 5: # thumb_right
            if HandPosition.LEFT_START2 in self:
                hand.position = HandPosition.RIGHT_END2
            else:
                hand.position = HandPosition.RIGHT_START2

        elif hand.gesture == 4: # thumb_left
            if HandPosition.RIGHT_START2 in self:
                hand.position = HandPosition.LEFT_END2
            else:
                hand.position = HandPosition.LEFT_START2

        #SWIPE_RIGHT3 and SWIPE_LEFT3
        elif hand.gesture == 15: # two_right
            if HandPosition.LEFT_START3 in self:
                hand.position = HandPosition.RIGHT_END3
            else:
                hand.position = HandPosition.RIGHT_START3

        elif hand.gesture == 14: # two_left
            if HandPosition.RIGHT_START3 in self:
                hand.position = HandPosition.LEFT_END3
            else:
                hand.position = HandPosition.LEFT_START3
        
        #SWIPE_UP3 and SWIPE_DOWN3
        elif hand.gesture == 39: # two_up
            if HandPosition.DOWN_START3 in self:
                hand.position = HandPosition.UP_END3
            else:
                hand.position = HandPosition.UP_START3

        elif hand.gesture == 16: # two_down
            if HandPosition.UP_START3 in self:
                hand.position = HandPosition.DOWN_END3
            else:
                hand.position = HandPosition.DOWN_START3

        #SWIPE_UP2 and SWIPE_DOWN2
        elif hand.gesture == 6: # thumb_down
            if HandPosition.ZOOM_OUT_START in self:
                hand.position = HandPosition.DOWN_END2
            else:
                hand.position = HandPosition.UP_START2
        else:
            hand.position = HandPosition.UNKNOWN

    #where gestures are recognized as actions!!!!
    def check_is_action(self,x):
        """
        Check if gesture is action.
        
        x : Hand #Hand object.

        Returns: bool #True if gesture is action.
        """
        if self.is_swipe_left(x): return True
        if self.is_swipe_right(x): return True
        if self.is_swipe_up(x): return True
        if self.is_swipe_down(x): return True
        if self.is_drag2(x): return True
        if self.is_drop2(x): return True
        if self.is_drag3(x): return True
        if self.is_drop3(x): return True
        if self.is_fast_swipe_up(x): return True
        if self.is_fast_swipe_down(x): return True
        if self.is_zoom_in(x): return True
        if self.is_zoom_out(x): return True
        if self.is_swipe_left2(x): return True
        if self.is_swipe_right2(x): return True
        if self.is_swipe_left3(x): return True
        if self.is_swipe_right3(x): return True
        if self.is_swipe_up3(x): return True
        if self.is_swipe_down3(x): return True
        if self.is_drag(x): return True
        if self.is_tap_or_double_tap(x): return True
        if self.is_swipe_down2(x): return True
        if self.is_swipe_up2(x): return True
        if self.is_drop(x): return True
        return False
    
    #function for all the actions, so instead of repeating in each, do this
    def set_action(self, event):
        self.action = event
        self.clear()
        
    
    def is_swipe_left(self, x):
        #SWIPE LEFT EVENT= hand_right -> hand_left (RIGHT_START -> LEFT_END)
        if x.position == HandPosition.LEFT_END and HandPosition.RIGHT_START in self:
            start_index = self.index_position(HandPosition.RIGHT_START)
            if (self.swipe_distance(self._deque[start_index], x)
                and self.check_duration(start_index)
                and self.check_horizontal_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_LEFT)
                return True
            else:
                self.clear()
                
    def is_swipe_right(self, x):
        #SWIPE RIGHT EVENT = hand_left -> hand_right (LEFT_START -> RIGHT_END)
        if x.position == HandPosition.RIGHT_END and HandPosition.LEFT_START in self:
            start_index = self.index_position(HandPosition.LEFT_START)
            if (self.swipe_distance(self._deque[start_index], x)
                and self.check_duration(start_index)
                and self.check_horizontal_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_RIGHT)
                return True
            else:
                self.clear()
    
    def is_swipe_up(self, x):
        #SWIPE UP EVENT: hand_down -> stop/palm/stop_inv (DOWN_START -> UP_END)
        if x.position == HandPosition.UP_END and HandPosition.DOWN_START in self:
            start_index = self.index_position(HandPosition.DOWN_START)
            if (self.swipe_distance(self._deque[start_index], x)
                and self.check_duration(start_index)
                and self.check_vertical_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_UP)
                return True
            else:
                self.clear()
                
    def is_swipe_down(self, x):
        #SWIPE DOWN EVENT= stop/palm/stop_inv -> hand_down (UP_START -> DOWN_END)
        if x.position == HandPosition.DOWN_END and HandPosition.UP_START in self:
            start_index = self.index_position(HandPosition.UP_START)
            if (self.swipe_distance(self._deque[start_index], x)
                and self.check_duration(start_index)
                and self.check_vertical_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_DOWN)
                return True
            else:
                self.clear()
    
        
    def is_drag2(self, x):
        #DRAG2 triggered by holding a gesture like grip or fist: grip-> part_hand_heart2
        if x.gesture == 18 and self.action is None: # grip
            start_index = self.index_gesture(18)
            if self.check_duration(start_index):
                self.set_action(Event.DRAG2)
                return True
    
    def is_drop2(self, x):
        #DROP2= grip-> part_hand_heart2/part_hand_heart #DRAG2=grip
        if self.action == Event.DRAG2 and x.gesture in [11, 12]: # hand heart
            self.set_action(Event.DROP2)
            return True
        return False
        
    def is_drag3(self, x):
        #DRAG3= part_hand_heart -> ok
        if x.gesture == 29 and self.action is None: #ok
            start_index = self.index_gesture(29)
            if self.check_duration(start_index):
                self.set_action(Event.DRAG3)
                return True
        return False
    
    def is_drop3(self, x):
        #DROP3= ok -> part_hand_heart/part_hand_heart2
        if self.action == Event.DRAG3 and x.gesture in [11, 12]: # hand heart
            self.set_action(Event.DROP3)
            return True
        return False
        
    def is_fast_swipe_up(self, x):
        #FAST_SWIPE_UP= point -> one (FAST_SWIPE_UP_START -> FAST_SWIPE_UP_END)
        if x.position == HandPosition.FAST_SWIPE_UP_END and HandPosition.FAST_SWIPE_UP_START in self:
            start_index = self.index_position(HandPosition.FAST_SWIPE_UP_START)
            if (self.check_duration(start_index, min_frames=20)
                and self.check_vertical_swipe(self._deque[start_index], x)):
                self.set_action(Event.FAST_SWIPE_UP)
                return True
            else:
                self.clear()
        return False
        
    def is_fast_swipe_down(self, x):
        #FAST_SWIPE_DOWN= one -> point (FAST_SWIPE_DOWN_START -> FAST_SWIPE_DOWN_END)
        if x.position == HandPosition.FAST_SWIPE_DOWN_END and HandPosition.FAST_SWIPE_DOWN_START in self:
            start_index = self.index_position(HandPosition.FAST_SWIPE_DOWN_START)
            if (self.check_duration(start_index, min_frames=20)
                and self.check_vertical_swipe(self._deque[start_index], x)):
                self.set_action(Event.FAST_SWIPE_DOWN)
                return True
        return False
    
    def is_zoom_in(self, x):
        #ZOOM_IN= fist -> thumb_index/three2
        if x.position == HandPosition.ZOOM_IN_END and HandPosition.ZOOM_IN_START in self:
            start_index = self.index_position(HandPosition.ZOOM_IN_START)
            if (self.check_duration(start_index, min_frames=20)
                and self.check_vertical_swipe(self._deque[start_index], x)
                and self.check_horizontal_swipe(self._deque[start_index], x)):
                self.set_action(Event.ZOOM_IN)
                return True
    
    def is_zoom_out(self, x):
        #ZOOM_OUT= thumb_index/three2 -> fist
        if x.position == HandPosition.ZOOM_OUT_END and HandPosition.ZOOM_OUT_START in self:
            start_index = self.index_position(HandPosition.ZOOM_OUT_START)
            if (self.check_duration(start_index, min_frames=20)
                and self.check_vertical_swipe(self._deque[start_index], x)
                and self.check_horizontal_swipe(self._deque[start_index], x)):
                self.set_action(Event.ZOOM_OUT)
                return True
            else:
                self.clear()
        return False

    def is_swipe_left2(self, x):
        #SWIPE_LEFT2= thumb_right -> thumb_left (RIGHT_START2 -> LEFT_END2)
        if x.position == HandPosition.LEFT_END2 and HandPosition.RIGHT_START2 in self:
            start_index = self.index_position(HandPosition.RIGHT_START2)
            if (self.swipe_distance(self._deque[start_index], x)
                and self.check_duration(start_index)
                and self.check_horizontal_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_LEFT2)
                return True
            else:
                self.clear()
        return False
    
    def is_swipe_right2(self, x):
        #SWIPE_RIGHT2= thumb_left -> thumb_right (LEFT_START2 -> RIGHT_END2)
        if x.position == HandPosition.RIGHT_END2 and HandPosition.LEFT_START2 in self:
            start_index = self.index_position(HandPosition.LEFT_START2)
            if (self.swipe_distance(self._deque[start_index], x)
                and self.check_duration(start_index)
                and self.check_horizontal_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_RIGHT2)
                return True
            else:
                self.clear()
        return False
    
    def is_swipe_left3(self, x):
        #SWIPE_LEFT3= two_right -> two_left (RIGHT_START3 -> LEFT_END3)
        if x.position == HandPosition.LEFT_END3 and HandPosition.RIGHT_START3 in self:
            start_index = self.index_position(HandPosition.RIGHT_START3)
            if (self.swipe_distance(self._deque[start_index], x)
                and self.check_duration(start_index)
                and self.check_horizontal_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_LEFT3) # two
                return True
            else:
                self.clear()
        return False
        
    def is_swipe_right3(self, x):
        #SWIPE_RIGHT3= two_left -> two_right (LEFT_START3 -> RIGHT_END3)
        if x.position == HandPosition.RIGHT_END3 and HandPosition.LEFT_START3 in self:
            start_index = self.index_position(HandPosition.LEFT_START3)
            if (self.swipe_distance(self._deque[start_index], x)
                and self.check_duration(start_index)
                and self.check_horizontal_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_RIGHT3)
                return True
            else:
                self.clear()
        return False
        
    def is_swipe_up3(self, x):
        #SWIPE_UP3 = two_down -> two_up (DOWN_START3 -> UP_END3)
        if x.position == HandPosition.UP_END3 and HandPosition.DOWN_START3 in self:
            start_index = self.index_position(HandPosition.DOWN_START3)
            if (self.check_duration(start_index, min_frames=15)
                and self.check_vertical_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_UP3)
                return True
            else:
                self.clear()
        return False
        
    def is_swipe_down3(self, x):
        #SWIPE_DOWN3= two_up -> two_down (UP_START3 -> DOWN_END3)
        if x.position == HandPosition.DOWN_END3 and HandPosition.UP_START3 in self:
            start_index = self.index_position(HandPosition.UP_START3)
            if (self.check_duration(start_index, min_frames=15)
                and self.check_vertical_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_DOWN3)
                return True
            else:
                self.clear()
        return False
        
    def is_drag(self, x):
        #DRAG= palm -> grabbing -> fist
        if HandPosition.DRAG_START in self and x.gesture == 25 and self.action is None: # fist
            start_index = self.index_gesture(17) # grabbing
            if self.check_duration(start_index, min_frames=3):
                self.set_action(Event.DRAG)
                return True
            else:
                self.clear()
        return False
    
    def is_tap_or_double_tap(self, x):
        #TAP= fist -> fist_inverted -> point
        #DOUBLE_TAP = (fist -> fist_inverted -> point -> fist -> fist_inverted -> point)
        if HandPosition.ZOOM_IN_START in self and x.gesture == 19: # point
            start_index = self.index_position(HandPosition.ZOOM_IN_START)
            if (self.check_duration(start_index, min_frames=8)
                and self.check_vertical_swipe(self._deque[start_index], x)
                and self.check_horizontal_swipe(self._deque[start_index], x)):
                self.set_action(Event.TAP)
                return True
            elif (self.check_duration(start_index, min_frames=2)
                and self.check_duration_max(start_index, max_frames=8)
                and self.check_vertical_swipe(self._deque[start_index], x)
                and self.check_horizontal_swipe(self._deque[start_index], x)):
                self.action_deque.append(Event.TAP)
                if len(self.action_deque) >= 2 and self.action_deque[-1] == Event.TAP and self.action_deque[-2] == Event.TAP:
                    self.action_deque.pop()
                    self.action_deque.pop()
                    self.set_action(Event.DOUBLE_TAP)
                    return True
        return False
    
    def is_swipe_down2(self, x):
        #SWIPE_DOWN2= thumb_index/three2 -> thumb_down (ZOOM_OUT_START -> DOWN_END2)
        if x.position == HandPosition.DOWN_END2 and HandPosition.ZOOM_OUT_START in self:
            start_index = self.index_position(HandPosition.ZOOM_OUT_START)
            if (self.swipe_distance(self._deque[start_index], x)
                and self.check_vertical_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_DOWN2)
                return True
            else:
                self.clear()
        return False
    
    def is_swipe_up2(self, x):
        #SWIPE_UP2 = thumb_down -> thumb_index/three2 (UP_START2 -> ZOOM_OUT_START)
        if x.position == HandPosition.ZOOM_OUT_START and HandPosition.UP_START2 in self:
            start_index = self.index_position(HandPosition.UP_START2)
            if (self.swipe_distance(self._deque[start_index], x)
                and self.check_vertical_swipe(self._deque[start_index], x)):
                self.set_action(Event.SWIPE_UP2)
                return True
            else:
                self.clear()
        return False
    
    def is_drop(self, x):
        #DROP = (fist -> grabbing -> palm)
        if self.action == Event.DRAG and x.gesture in [35, 31, 36, 17]: # [stop, palm, stop_inverted, grabbing]
            self.set_action(Event.DROP)
            return True
        return False
    
    def clear(self):
        self._deque.clear()

    def copy(self):
        return self._deque.copy()

    def count(self, x):
        return self._deque.count(x)

    def extend(self, iterable):
        self._deque.extend(iterable)

    def insert(self, i, x):
        self._deque.insert(i, x)

    def pop(self):
        return self._deque.pop()

    def remove(self, value):
        self._deque.remove(value)

    def reverse(self):
        self._deque.reverse()

    def __str__(self):
        return f"Deque({[hand.gesture for hand in self._deque]})"
