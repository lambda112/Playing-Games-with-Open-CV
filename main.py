import cv2 as cv
import mediapipe as mp
import direct_input as pydirectinput
from multiprocessing.pool import ThreadPool
from button_config import button_block

# pools
CAMERA_POOL = ThreadPool(processes=1)
HAND_POOL = ThreadPool(processes=1)
INPUT_POOL = ThreadPool(processes=1)

# setup hand tracking
mp_hands = mp.solutions.hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# video footage
cap = cv.VideoCapture(0)

# setup input
pydirectinput.PAUSE = 0.003
INPUT_KEYS = ["wd", "w", "wa", "d", "a", "sd", "s", "sa"]

# frames for multiprocess
def get_frames():
    rec, frame = cap.read()
    return rec, frame

def left_hand_input(thumb_pos, index_pos, middle_pos, ring_pos, pinky_pos):
    X_THRESHOLD = 25
    Y_THRESHOLD = 20

    if thumb_pos:
        if index_pos:
            if abs(thumb_pos[0] - index_pos[0]) < X_THRESHOLD and abs(thumb_pos[1] - index_pos[1]) < Y_THRESHOLD:
                pydirectinput.hotkey("w")
                print("pressed w")
        if middle_pos:
            if abs(thumb_pos[0] - middle_pos[0]) < X_THRESHOLD and abs(thumb_pos[1] - middle_pos[1]) < Y_THRESHOLD:
                pydirectinput.hotkey("a")
                print("pressed a")
        if ring_pos:
            if abs(thumb_pos[0] - ring_pos[0]) < X_THRESHOLD and abs(thumb_pos[1] - ring_pos[1]) < Y_THRESHOLD:
                pydirectinput.hotkey("s")
                print("pressed s")
        if pinky_pos:
            if abs(thumb_pos[0] - pinky_pos[0]) < X_THRESHOLD and abs(thumb_pos[1] - pinky_pos[1]) < Y_THRESHOLD:
                pydirectinput.hotkey("r")
                print("pressed r")

# get input based on hand movement
def get_input(point_list:list):

    try:
        thumb_pos = point_list[0]
        index_pos = point_list[1]
        middle_pos = point_list[2]
        ring_pos = point_list[3]
        pinky_pos = point_list[4]
        left_hand_input(thumb_pos, index_pos, middle_pos, ring_pos, pinky_pos)

    except IndexError:
        None

# display handtracking get coords
def hand_tracking(results):
    h,w,_ = frame.shape
    index_finger_tip = None
    index_finger = []

    for hand_index, hand in enumerate(results.multi_hand_landmarks):
        mp_drawing.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
        point_pos = []

        index_finger_tip = hand.landmark[8]
        cx,cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
        index_finger_tip = (cx,cy)
        index_finger.append(index_finger_tip)

        for index, pos in enumerate(hand.landmark):
            if index in [4, 8, 12, 16, 20]:
                cx,cy = int(pos.x * w), int(pos.y * h)
                point_pos.append((cx,cy))
    

    INPUT_POOL.apply_async(get_input, args=(point_pos, ))

    if index_finger_tip:
        return index_finger
    

def draw_boxes(frame, index_hand = None):
    buttons = button_block(frame.shape[1], frame.shape[0])
    for index, (topl, botr) in enumerate(buttons.values()):
        topl
        cv.rectangle(frame, topl, botr, (0,0,255), 2, cv.LINE_4)
        cv.putText(frame, f"button{index}", (topl[0], topl[1]+20), cv.FONT_HERSHEY_COMPLEX, 0.4, (0,255,0), 1) 

        for tip in index_hand:
            finger_x = tip[0]
            finger_y = tip[1]
            box_top_x = topl[0]
            box_bottom_x = botr[0]
            box_top_y = topl[1]
            box_bottom_y = botr[1]

            if box_bottom_y > finger_y > box_top_y and box_bottom_x > finger_x > box_top_x:
                pydirectinput.hotkey(INPUT_KEYS[index])
                print(f"Working {INPUT_KEYS[index]}")


# process image for tracking 
def image_processing(frame):
    frame = cv.flip(frame, 1) # t
    frame = cv.GaussianBlur(frame, (5,5), 1)
    frame = cv.dilate(frame, (5,5), iterations=1)
    frame = cv.erode(frame, (5,5), iterations=1)
    return frame

# video loop
while True:
    # get frame
    _, frame = CAMERA_POOL.apply_async(get_frames).get()
    frame = image_processing(frame)
    
    # track hand
    results = mp_hands.process(cv.cvtColor(frame, cv.COLOR_BGR2RGB))
    if results.multi_hand_landmarks:
        hand_result = HAND_POOL.apply_async(hand_tracking, args=(results,)).get()
        draw_boxes(frame, hand_result)

    # show frame
    cv.imshow("frame", frame)
    if cv.waitKey(1) == ord("q") & 0xFF:
        break
    

cv.destroyAllWindows()
cap.release()
