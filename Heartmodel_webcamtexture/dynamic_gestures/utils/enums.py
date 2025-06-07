from enum import Enum

# Hand position enum.
#low-level, frame-by-frame info about where a hand starts or ends in motion.
#describing transitions in movement, detecting gestures over time
class HandPosition(Enum):
    UNKNOWN = -1
    LEFT_START = 1
    RIGHT_START = 2
    LEFT_END = 3
    RIGHT_END = 4
    UP_START = 5
    UP_END = 6
    DOWN_START = 7
    DOWN_END = 8
    ZOOM_IN_START = 13
    ZOOM_IN_END = 14
    ZOOM_OUT_START = 15
    ZOOM_OUT_END = 16
    DRAG_START = 25
    DRAG_END = 26
    LEFT_START3 = 27
    RIGHT_START3 = 28
    LEFT_END3 = 29
    RIGHT_END3 = 30
    DOWN_START3 = 31
    DOWN_END3 = 32
    UP_START3 = 33
    UP_END3 = 34


# Events for action controller
#high-level gestures that have been recognized
class Event(Enum):
    UNKNOWN = -1
    SWIPE_RIGHT = 0
    SWIPE_LEFT = 1
    SWIPE_UP = 2
    SWIPE_DOWN = 3
    DRAG = 4
    DROP = 5
    ZOOM_IN = 8
    ZOOM_OUT = 9
    DOUBLE_TAP = 14
    SWIPE_RIGHT3 = 15
    SWIPE_LEFT3 = 16
    SWIPE_UP3 = 17
    SWIPE_DOWN3 = 18
    TAP = 23

#static hand poses or target shapes detected by the hand model
targets = [
    'hand_down',
    'hand_right',
    'hand_left',
    'thumb_index',
    'thumb_left',
    'thumb_right',
    'thumb_down',
    'half_up',
    'half_left',
    'half_right',
    'half_down',
    'part_hand_heart',
    'part_hand_heart2',
    'fist_inverted',
    'two_left',
    'two_right',
    'two_down',
    'grabbing',
    'grip',
    'point',
    'call',
    'three3',
    'little_finger',
    'middle_finger',
    'dislike',
    'fist',
    'four',
    'like',
    'mute',
    'ok',
    'one',
    'palm',
    'peace',
    'peace_inverted',
    'rock',
    'stop',
    'stop_inverted',
    'three',
    'three2',
    'two_up',
    'two_up_inverted',
    'three_gun',
    'one_left',
    'one_right', 
    'one_down'
 ]
