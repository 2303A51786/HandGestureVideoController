import time
import pyautogui
from utils import calculate_distance

class GestureController:
    """
    A class to translate detected hand finger states and landmark coordinates 
    into system keyboard inputs (Play/Pause, Forward, Rewind, and Volume Control).
    """
    def __init__(self):
        # Fail-safe feature: If you quickly drag the mouse pointer to any corner of the screen,
        # PyAutoGUI will raise a FailSafeException, stopping the execution.
        # This is a safety measure to prevent automation scripts from running out of control.
        pyautogui.FAILSAFE = True

        # Track times to prevent a single gesture from double-triggering rapid keypresses
        self.last_action_time = 0
        
        # Cooldown periods in seconds
        self.cooldown_press = 1.0  # Cooldown for discrete keys (like Play/Pause)
        self.cooldown_seek = 0.8   # Cooldown for seeking (Forward/Rewind)

        # Variables for volume tracking
        self.prev_volume_dist = None
        self.volume_threshold = 8.0  # Minimum pixel movement required to trigger volume changes

    def process_gestures(self, fingers, lm_list):
        """
        Analyzes finger status and coordinates to trigger keyboard controls.
        
        Parameters:
        - fingers (list): Binary list representing finger state [Thumb, Index, Middle, Ring, Pinky] (1 = open, 0 = closed)
        - lm_list (list): Coordinate position list of all 21 hand landmarks [[id, x, y], ...]
        
        Returns:
        - str: A label representing the action triggered, which we will display on the screen.
        """
        current_time = time.time()

        # If no landmarks are detected, return empty state
        if not lm_list or len(lm_list) < 21:
            self.prev_volume_dist = None
            return "No Hand Detected"

        # ----------------------------------------------------
        # 1. GESTURE: PLAY / PAUSE (Victory sign: Index & Middle up, others down)
        # ----------------------------------------------------
        if fingers == [0, 1, 1, 0, 0]:
            # Reset volume tracking since we're in a different mode
            self.prev_volume_dist = None
            
            # Check if enough time has passed since the last action to prevent spamming
            if current_time - self.last_action_time > self.cooldown_press:
                # Simulates pressing the spacebar (common key for play/pause in media players)
                pyautogui.press('space')
                self.last_action_time = current_time
                return "PLAY/PAUSE (Space)"
            return "PLAY/PAUSE (Cooldown)"

        # ----------------------------------------------------
        # 2. GESTURE: FORWARD (3 fingers up: Index, Middle, Ring)
        # ----------------------------------------------------
        elif fingers == [0, 1, 1, 1, 0]:
            self.prev_volume_dist = None
            
            if current_time - self.last_action_time > self.cooldown_seek:
                # Simulates pressing the Right Arrow key (Fast Forward)
                pyautogui.press('right')
                self.last_action_time = current_time
                return "FORWARD (-->)"
            return "FORWARD (Cooldown)"

        # ----------------------------------------------------
        # 3. GESTURE: REWIND (Only 1 finger up: Index)
        # ----------------------------------------------------
        elif fingers == [0, 1, 0, 0, 0]:
            self.prev_volume_dist = None
            
            if current_time - self.last_action_time > self.cooldown_seek:
                # Simulates pressing the Left Arrow key (Rewind)
                pyautogui.press('left')
                self.last_action_time = current_time
                return "REWIND (<--)"
            return "REWIND (Cooldown)"

        # ----------------------------------------------------
        # 4. GESTURE: VOLUME CONTROL (Thumb and Index up, others closed)
        # ----------------------------------------------------
        elif fingers == [1, 1, 0, 0, 0]:
            # Extract coordinates for Thumb tip (id 4) and Index tip (id 8)
            # lm_list format: [id, x, y]. So index 1 is x, index 2 is y.
            thumb_tip = (lm_list[4][1], lm_list[4][2])
            index_tip = (lm_list[8][1], lm_list[8][2])

            # Calculate current distance between thumb tip and index tip in pixels
            current_dist = calculate_distance(thumb_tip, index_tip)

            # If this is the first frame entering volume mode, initialize baseline distance
            if self.prev_volume_dist is None:
                self.prev_volume_dist = current_dist
                return "VOLUME (Initializing)"

            # Calculate difference from the previous frame
            diff = current_dist - self.prev_volume_dist

            # If the distance increased beyond threshold: volume up
            if diff > self.volume_threshold:
                pyautogui.press('volumeup')
                self.prev_volume_dist = current_dist
                return "VOLUME UP (+)"
            # If the distance decreased below negative threshold: volume down
            elif diff < -self.volume_threshold:
                pyautogui.press('volumedown')
                self.prev_volume_dist = current_dist
                return "VOLUME DOWN (-)"

            return "VOLUME (Adjusting)"

        # ----------------------------------------------------
        # 5. NO ACTIVE GESTURE (Default State)
        # ----------------------------------------------------
        else:
            # Reset volume baseline to prevent large sudden volume shifts when re-entering the mode
            self.prev_volume_dist = None
            return "Active Listening..."
