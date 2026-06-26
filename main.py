import cv2
from hand_detector import HandDetector
from gesture_controller import GestureController
from utils import FPSCounter

def main():
    """
    Main program execution loop.
    Captures video from the webcam, runs hand landmark detection,
    translates hand shapes into playback commands, and renders a clean graphical HUD.
    """
    # 1. Initialize the Webcam Capture
    # 0 is usually the built-in webcam. If you have an external webcam, you might need to change it to 1 or 2.
    cap = cv2.VideoCapture(0)
    
    # Set the camera feed resolution (640x480 is standard and keeps performance high)
    cap.set(3, 640)
    cap.set(4, 480)

    # Safety check: if OpenCV cannot access the camera, stop execution
    if not cap.isOpened():
        print("\n[-] Error: Could not open the webcam.")
        print("[*] Troubleshooting tips:")
        print("    1. Verify your webcam is plugged in.")
        print("    2. Make sure no other application (like Zoom or Teams) is using the webcam.")
        print("    3. If you have an external camera, try changing 'cv2.VideoCapture(0)' to 'cv2.VideoCapture(1)'.\n")
        return

    # 2. Instantiate modules
    # max_hands=1 so we only track one hand (prevents confusing the controller)
    detector = HandDetector(max_hands=1, detection_con=0.7, track_con=0.7)
    controller = GestureController()
    fps_counter = FPSCounter()

    print("\n[+] Gesture Video Controller is running!")
    print("[*] Focus on the camera window and press 'q' to quit.\n")

    # Main video frame processing loop
    while True:
        # Read a frame from the webcam
        success, frame = cap.read()
        if not success:
            print("[-] Error: Failed to grab frame from camera.")
            break

        # Flip the frame horizontally. Webcams capture mirrored footage, so flipping it 
        # makes it feel natural like looking into a mirror.
        frame = cv2.flip(frame, 1)
        height, width, channels = frame.shape

        # 3. Detect Hands and draw landmarks
        # This draws the dots and lines on the 'frame' variable directly
        frame = detector.find_hands(frame, draw=True)
        
        # Get coordinates of the 21 joints
        lm_list = detector.find_position(frame, draw=False)

        # 4. Check for active gestures
        action_label = "Active Listening..."
        if lm_list:
            # Check which fingers are up
            fingers = detector.fingers_up()
            
            # Send hand state to the controller to press keys and get back active action name
            action_label = controller.process_gestures(fingers, lm_list)

        # 5. Calculate frame rate performance
        fps = fps_counter.get_fps()

        # ----------------------------------------------------
        # AESTHETICS: Transparent Overlay HUD (Heads-Up Display)
        # ----------------------------------------------------
        # To draw a semi-transparent HUD, we create a copy of the frame, draw solid shapes,
        # and blend them back with transparency.
        hud_overlay = frame.copy()
        
        # Draw dark top status bar
        cv2.rectangle(hud_overlay, (0, 0), (width, 65), (20, 20, 20), cv2.FILLED)
        
        # Draw dark bottom instructions bar
        cv2.rectangle(hud_overlay, (0, height - 45), (width, height), (30, 30, 30), cv2.FILLED)
        
        # Blend the overlay at 45% opacity
        cv2.addWeighted(hud_overlay, 0.45, frame, 0.55, 0, frame)

        # ----------------------------------------------------
        # RENDER TEXT & VISUAL FEEDBACK
        # ----------------------------------------------------
        # Draw "STATUS:" label
        cv2.putText(frame, "STATUS:", (15, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Dynamic color coding for the status label based on action
        if "PLAY" in action_label or "FORWARD" in action_label or "VOLUME UP" in action_label:
            text_color = (0, 255, 100)      # Bright neon green
        elif "REWIND" in action_label or "VOLUME DOWN" in action_label:
            text_color = (0, 180, 255)      # Bright neon orange-yellow
        elif "No Hand" in action_label:
            text_color = (130, 130, 130)    # Muted gray
        else:
            text_color = (255, 0, 180)      # Neon pink/purple (Listening mode)

        # Draw the active action text next to STATUS:
        cv2.putText(frame, action_label, (115, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)

        # Draw the FPS counter in the top right
        cv2.putText(frame, f"FPS: {fps}", (width - 135, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Draw the bottom instruction helper line
        instructions = "Victory = Play/Pause | 3 Fingers = FFWD | Index = Rewind | Thumb+Index = Vol"
        cv2.putText(frame, instructions, (15, height - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)

        # 6. Display the final processed window
        cv2.imshow("Hand Gesture Video Controller", frame)

        # 7. Listen for Keyboard Inputs on OpenCV Window
        # cv2.waitKey(1) checks for user key presses every 1 millisecond.
        # If 'q' is pressed, it breaks the loop to shut down.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 8. Clean up Camera and Windows
    cap.release()
    cv2.destroyAllWindows()
    print("[+] Program closed. Thank you for using Gesture Controller!")

if __name__ == "__main__":
    main()
