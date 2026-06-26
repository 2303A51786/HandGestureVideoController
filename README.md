# Hand Gesture Video Controller 🎥🖐️

An interactive computer vision project built with Python 3.11, OpenCV, and MediaPipe. This project allows you to control media playback (Play/Pause, Fast Forward, Rewind, and Volume Control) in real-time on your computer using simple hand gestures captured through your webcam.

---

## 🌟 Features

*   **Real-time Hand Tracking**: Powered by Google's MediaPipe Hands model to detect and track 21 hand landmarks.
*   **Intuitive Gesture Controls**:
    *   ✌️ **Victory Sign (Index & Middle Up)**: Play / Pause (Simulates `Spacebar`).
    *   🤟 **3 Fingers Up (Index, Middle, Ring)**: Fast Forward (Simulates `Right Arrow`).
    *   ☝️ **Index Finger Up**: Rewind (Simulates `Left Arrow`).
    *   🤏 **Thumb & Index Finger Up (Pinch)**: Adjust Volume (Pinch closer for Volume Down, spread wider for Volume Up).
*   **Color-Coded HUD (Heads-Up Display)**: Modern transparent overlay showing the FPS and real-time status of your gestures.
*   **Failsafe Feature**: Quickly drag the mouse cursor to any corner of the screen to stop the program instantly.
*   **Universal Compatibility**: Works across operating systems (Windows, Mac, Linux) and controls any active player in the foreground (VLC, YouTube, Netflix, Windows Media Player, Spotify).

---

## 📂 Project Structure

```text
video-through-hand/
│
├── main.py               # Main loop, webcam capture, UI rendering, and exit conditions.
├── hand_detector.py      # HandDetector class wrapping MediaPipe Hands & finger state calculations.
├── gesture_controller.py # GestureController class converting finger states to PyAutoGUI keystrokes.
├── utils.py              # Math helper functions (Euclidean distance, value mapping, FPS tracker).
├── requirements.txt      # List of project dependencies.
└── README.md             # Project documentation.
```

---

## 🛠️ Installation & Setup

Follow these simple steps to set up and run the project:

### 1. Prerequisites
Ensure you have **Python 3.11** installed on your system. 

### 2. Clone or Create Project Folder
Open your VS Code terminal and make sure you are in the project folder:
`c:\Users\CHAITRA REDDY\OneDrive\Desktop\py project hand`

### 3. Set Up Virtual Environment (Recommended)
Creating a virtual environment isolates your project libraries:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 4. Install Dependencies
Install all required libraries using the terminal command:
```powershell
pip install -r requirements.txt
```

---

## 🚀 How to Use

1.  Open any media player (such as a YouTube video in your browser or a video in VLC Media Player).
2.  Start the Python program:
    ```powershell
    python main.py
    ```
3.  A window titled **"Hand Gesture Video Controller"** will pop up displaying your webcam feed.
4.  **Click on your media player window (e.g., Chrome or VLC) to bring it into focus.** (Since the program simulates keyboard presses, the player must be the active window on your screen to receive them).
5.  Raise your hand to the webcam and perform gestures:
    *   **Play/Pause**: Raise the Index and Middle fingers (peace sign).
    *   **Forward**: Raise the Index, Middle, and Ring fingers.
    *   **Rewind**: Raise only the Index finger.
    *   **Volume Control**: Raise only the Thumb and Index finger. Spread them apart to turn the volume up, pinch them together to turn the volume down.
6.  To quit the program, focus on the camera window and press the **'q'** key.

---

## ⚙️ How It Works (Behind the Scenes)

1.  **Frame Capture**: `main.py` reads a frame from the webcam using `cv2.VideoCapture` and mirrors it horizontally for natural feedback.
2.  **Hand Processing**: The frame is sent to `hand_detector.py` where MediaPipe detects the presence of a hand.
3.  **Coordinate Conversion**: Landmark values are converted from normalized percentages to actual pixel values.
4.  **Finger Counting**: The program checks finger tips against joint values to determine which fingers are upright.
5.  **Gesture Mapping**: `gesture_controller.py` evaluates the finger states and triggers simulated keypresses using `pyautogui`.
6.  **HUD Rendering**: The final frame is layered with a semi-transparent HUD overlay displaying the real-time program status and frame rate.
