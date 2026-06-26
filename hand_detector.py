import cv2
import mediapipe as mp

class HandDetector:
    """
    A modular class to detect hands and extract landmark coordinates 
    using Google's MediaPipe library.
    """
    def __init__(self, mode=False, max_hands=1, detection_con=0.5, track_con=0.5):
        """
        Initializes the MediaPipe Hands model.
        
        Parameters:
        - mode (bool): If True, treats input images as static photos (slower). If False, treats as video stream (faster).
        - max_hands (int): Maximum number of hands to detect at one time.
        - detection_con (float): Minimum confidence value ([0.0, 1.0]) for hand detection to be considered successful.
        - track_con (float): Minimum confidence value ([0.0, 1.0]) for tracking landmarks in consecutive frames.
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        # 1. Initialize MediaPipe Hands solution
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        
        # 2. Initialize MediaPipe Drawing utilities (to draw lines and points on our frame)
        self.mp_draw = mp.solutions.drawing_utils
        
        # Stores the output results of the processing
        self.results = None
        self.lm_list = []

    def find_hands(self, img, draw=True):
        """
        Processes a BGR image to find hands and optionally draws the landmarks.
        
        Parameters:
        - img: The current frame from OpenCV (BGR color format).
        - draw (bool): If True, draws connections and dots on the hands.
        
        Returns:
        - img: The modified image with drawings (or original if draw=False).
        """
        # OpenCV captures images in BGR format, but MediaPipe requires RGB.
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process the image and find hands
        self.results = self.hands.process(img_rgb)
        
        # If hands are found in the frame
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    # Draw the 21 dots and connecting lines
                    self.mp_draw.draw_landmarks(
                        img, hand_lms, self.mp_hands.HAND_CONNECTIONS
                    )
        return img

    def find_position(self, img, hand_no=0, draw=False):
        """
        Extracts the pixel coordinates (x, y) of the 21 landmarks for a specific hand.
        
        Parameters:
        - img: The current frame (needed to get image width and height).
        - hand_no (int): The index of the hand to track (0 for first hand, 1 for second).
        - draw (bool): If True, draws a custom circle on the landmarks.
        
        Returns:
        - list: A list of 21 landmarks, where each item is [id, x, y].
        """
        self.lm_list = []
        
        if self.results.multi_hand_landmarks:
            # Check if the requested hand number is actually detected
            if len(self.results.multi_hand_landmarks) > hand_no:
                selected_hand = self.results.multi_hand_landmarks[hand_no]
                height, width, channels = img.shape
                
                # Loop through all 21 landmarks of the hand
                for id, lm in enumerate(selected_hand.landmark):
                    # lm.x and lm.y are normalized coordinates between 0.0 and 1.0.
                    # We multiply them by the image width and height to get actual pixel positions.
                    cx, cy = int(lm.x * width), int(lm.y * height)
                    self.lm_list.append([id, cx, cy])
                    
                    if draw:
                        # Draw a custom circle on each landmark point
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
                        
        return self.lm_list

    def fingers_up(self):
        """
        Determines which of the 5 fingers are currently open (up) or closed (down).
        
        Returns:
        - list: A list of 5 integers (0 for closed, 1 for open) representing [Thumb, Index, Middle, Ring, Pinky].
        """
        fingers = []
        
        # If landmarks list is empty or incomplete, assume all fingers are closed
        if not self.lm_list or len(self.lm_list) < 21:
            return [0, 0, 0, 0, 0]

        # 1. Check the Thumb
        # Handedness tells us if the hand is Left or Right
        if self.results.multi_handedness:
            # Get the classification label: 'Left' or 'Right'
            hand_label = self.results.multi_handedness[0].classification[0].label
            
            # The thumb moves horizontally. If the tip (id 4) is outer to the joint (id 3):
            # If the image is mirrored (default webcam), the labels might feel reversed:
            if hand_label == "Right":
                # For Right hand, thumb is open if tip x-coordinate is less than joint x-coordinate
                if self.lm_list[4][1] < self.lm_list[3][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else:
                # For Left hand, thumb is open if tip x-coordinate is greater than joint x-coordinate
                if self.lm_list[4][1] > self.lm_list[3][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        else:
            # Fallback check (simple horizontal comparison)
            if self.lm_list[4][1] > self.lm_list[3][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        # 2. Check the other 4 fingers (Index, Middle, Ring, Pinky)
        # Tip ids: Index (8), Middle (12), Ring (16), Pinky (20)
        # Joint ids: Index PIP joint (6), Middle PIP joint (10), Ring PIP joint (14), Pinky PIP joint (18)
        tip_ids = [8, 12, 16, 20]
        joint_ids = [6, 10, 14, 18]

        for tip, joint in zip(tip_ids, joint_ids):
            # In computer vision, the y-axis starts at 0 at the top and goes down.
            # So, if a finger tip is UP, its y-coordinate is SMALLER than its joint's y-coordinate.
            if self.lm_list[tip][2] < self.lm_list[joint][2]:
                fingers.append(1)  # Finger is open
            else:
                fingers.append(0)  # Finger is closed

        return fingers
