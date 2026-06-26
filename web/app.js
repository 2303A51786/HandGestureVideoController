// ==========================================================================
// CORE JAVASCRIPT LOGIC - GESTURE.IO WEB APP
// ==========================================================================

// 1. Get references to HTML elements in the DOM
const videoPlayer = document.getElementById('video-player');
const webcamElement = document.getElementById('webcam');
const canvasElement = document.getElementById('canvas-overlay');
const canvasCtx = canvasElement.getContext('2d');
const statusText = document.getElementById('status-text');
const fpsText = document.getElementById('fps-text');
const actionOverlay = document.getElementById('action-overlay');

// Volume UI Elements
const volumeCard = document.getElementById('volume-card');
const volumeBarFill = document.getElementById('volume-bar-fill');
const volumePercent = document.getElementById('volume-percent');

// 2. State Variables for tracking gestures and throttling (cooldowns)
let lastActionTime = 0;
const COOLDOWN_PRESS = 1000; // 1 second cooldown for play/pause toggles
const COOLDOWN_SEEK = 800;   // 0.8 second cooldown for forward/rewind seeks

// Volume tracking state
let prevVolumeDist = null;
const VOLUME_THRESHOLD = 0.02; // Normalized coordinate distance change threshold

// FPS calculation variables
let lastFrameTime = performance.now();

// 3. Action Notification overlay helper
let overlayTimeout = null;
function showActionOverlay(text) {
    actionOverlay.innerText = text;
    actionOverlay.classList.remove('action-overlay-hidden');
    
    // Clear any existing timeout to avoid overlap bugs
    if (overlayTimeout) clearTimeout(overlayTimeout);
    
    // Hide the text popup after 1 second
    overlayTimeout = setTimeout(() => {
        actionOverlay.classList.add('action-overlay-hidden');
    }, 1000);
}

// 4. Update the Volume Bar Visuals
function updateVolumeUI(volume) {
    const percent = Math.round(volume * 100);
    volumeBarFill.style.width = `${percent}%`;
    volumePercent.innerText = `${percent}%`;
    
    // Show the volume card overlay on screen
    volumeCard.classList.remove('volume-card-hidden');
}

// Hide the volume card after volume adjustments stop
let volumeHideTimeout = null;
function triggerVolumeHideTimeout() {
    if (volumeHideTimeout) clearTimeout(volumeHideTimeout);
    volumeHideTimeout = setTimeout(() => {
        volumeCard.classList.add('volume-card-hidden');
    }, 1500);
}

// 5. MediaPipe onResults callback (runs for every frame processed by the model)
function onResults(results) {
    // A. Calculate real-time FPS
    const currentTime = performance.now();
    const elapsed = currentTime - lastFrameTime;
    if (elapsed > 0) {
        const fps = 1000 / elapsed;
        fpsText.innerText = fps.toFixed(1);
    }
    lastFrameTime = currentTime;

    // B. Clear the canvas overlay drawing from the previous frame
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    // Draw the camera image on the canvas (mirrored horizontally)
    canvasCtx.translate(canvasElement.width, 0);
    canvasCtx.scale(-1, 1);
    canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
    canvasCtx.restore();

    // Check if any hands were detected
    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        // Set HUD Status to Active
        statusText.className = 'status-active';
        statusText.innerText = 'Hand Tracked';

        const landmarks = results.multiHandLandmarks[0];
        
        // Draw the MediaPipe dots and lines on the canvas overlay
        // Note: We use scale(-1, 1) to mirror drawings because we scaleX(-1) on canvas in CSS
        canvasCtx.save();
        drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {color: '#9d4edd', lineWidth: 3});
        drawLandmarks(canvasCtx, landmarks, {color: '#00f2fe', lineWidth: 1, radius: 4});
        canvasCtx.restore();

        // C. Calculate Finger states [Thumb, Index, Middle, Ring, Pinky] (1 = up, 0 = down)
        const fingers = [0, 0, 0, 0, 0];

        // 1. Check index, middle, ring, pinky fingers (comparing Y-coordinates)
        // Tip landmark ids: Index (8), Middle (12), Ring (16), Pinky (20)
        // Joint landmark ids: Index PIP (6), Middle PIP (10), Ring PIP (14), Pinky PIP (18)
        const tipIds = [8, 12, 16, 20];
        const jointIds = [6, 10, 14, 18];

        for (let i = 0; i < 4; i++) {
            // Y values range from 0.0 at the top to 1.0 at the bottom.
            // If tip Y is smaller than joint Y, the finger is open.
            if (landmarks[tipIds[i]].y < landmarks[jointIds[i]].y) {
                fingers[i + 1] = 1; 
            }
        }

        // 2. Check the Thumb (comparing X-coordinates based on Handedness)
        if (results.multiHandedness && results.multiHandedness.length > 0) {
            const isRightHand = results.multiHandedness[0].label === 'Right';
            
            // For right hand, if thumb tip x is less than joint x, it's open (outer-pointing)
            if (isRightHand) {
                if (landmarks[4].x < landmarks[3].x) fingers[0] = 1;
            } else {
                if (landmarks[4].x > landmarks[3].x) fingers[0] = 1;
            }
        }

        // D. Translate Finger states to Gestures
        const timeNow = Date.now();

        // ----------------------------------------------------
        // GESTURE 1: PLAY/PAUSE (Victory Sign: [0, 1, 1, 0, 0])
        // ----------------------------------------------------
        if (fingers[0] === 0 && fingers[1] === 1 && fingers[2] === 1 && fingers[3] === 0 && fingers[4] === 0) {
            prevVolumeDist = null;
            if (timeNow - lastActionTime > COOLDOWN_PRESS) {
                statusText.className = 'status-trigger';
                if (videoPlayer.paused) {
                    videoPlayer.play();
                    showActionOverlay("PLAY ▶️");
                    statusText.innerText = 'PLAY';
                } else {
                    videoPlayer.pause();
                    showActionOverlay("PAUSE ⏸️");
                    statusText.innerText = 'PAUSE';
                }
                lastActionTime = timeNow;
            }
        }
        // ----------------------------------------------------
        // GESTURE 2: FAST FORWARD (3 fingers raised: [0, 1, 1, 1, 0])
        // ----------------------------------------------------
        else if (fingers[0] === 0 && fingers[1] === 1 && fingers[2] === 1 && fingers[3] === 1 && fingers[4] === 0) {
            prevVolumeDist = null;
            if (timeNow - lastActionTime > COOLDOWN_SEEK) {
                statusText.className = 'status-trigger';
                videoPlayer.currentTime = Math.min(videoPlayer.duration, videoPlayer.currentTime + 10);
                showActionOverlay("FFWD +10s ⏩");
                statusText.innerText = 'FORWARD';
                lastActionTime = timeNow;
            }
        }
        // ----------------------------------------------------
        // GESTURE 3: REWIND (Only Index Finger up: [0, 1, 0, 0, 0])
        // ----------------------------------------------------
        else if (fingers[0] === 0 && fingers[1] === 1 && fingers[2] === 0 && fingers[3] === 0 && fingers[4] === 0) {
            prevVolumeDist = null;
            if (timeNow - lastActionTime > COOLDOWN_SEEK) {
                statusText.className = 'status-trigger';
                videoPlayer.currentTime = Math.max(0, videoPlayer.currentTime - 10);
                showActionOverlay("REWIND -10s ⏪");
                statusText.innerText = 'REWIND';
                lastActionTime = timeNow;
            }
        }
        // ----------------------------------------------------
        // GESTURE 4: VOLUME CONTROL (Thumb & Index up, others closed: [1, 1, 0, 0, 0])
        // ----------------------------------------------------
        else if (fingers[0] === 1 && fingers[1] === 1 && fingers[2] === 0 && fingers[3] === 0 && fingers[4] === 0) {
            statusText.innerText = 'Adjusting Volume';
            
            // Calculate distance between Thumb Tip (4) and Index Tip (8) in normalized coordinates
            const dx = landmarks[4].x - landmarks[8].x;
            const dy = landmarks[4].y - landmarks[8].y;
            const currentDist = Math.hypot(dx, dy);

            // Initialize baseline distance
            if (prevVolumeDist === null) {
                prevVolumeDist = currentDist;
            } else {
                const diff = currentDist - prevVolumeDist;

                // Adjust volume based on relative coordinate shifts
                if (diff > VOLUME_THRESHOLD) {
                    videoPlayer.volume = Math.min(1.0, videoPlayer.volume + 0.05);
                    prevVolumeDist = currentDist;
                    statusText.className = 'status-trigger';
                } else if (diff < -VOLUME_THRESHOLD) {
                    videoPlayer.volume = Math.max(0.0, videoPlayer.volume - 0.05);
                    prevVolumeDist = currentDist;
                    statusText.className = 'status-trigger';
                }
            }
            updateVolumeUI(videoPlayer.volume);
            triggerVolumeHideTimeout();
        }
        // Default listening state
        else {
            prevVolumeDist = null;
        }

    } else {
        // No hand is detected in the webcam
        statusText.className = 'status-listening';
        statusText.innerText = 'Active Listening...';
        prevVolumeDist = null;
    }
}

// 6. Initialize MediaPipe Hands model
const hands = new Hands({
    locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
    }
});

// Configure Hands options
hands.setOptions({
    maxNumHands: 1,
    modelComplexity: 1,
    minDetectionConfidence: 0.7,
    minTrackingConfidence: 0.7
});

// Bind output callback function
hands.onResults(onResults);

// 7. Setup the Webcam Camera feed loop
const camera = new Camera(webcamElement, {
    onFrame: async () => {
        // Send current webcam frame to MediaPipe Hands model for tracking
        await hands.send({image: webcamElement});
    },
    width: 640,
    height: 480
});

// Start the Camera and auto-play the sample video player (gently muted)
camera.start().then(() => {
    console.log("[+] Camera Started successfully!");
    videoPlayer.play();
    updateVolumeUI(videoPlayer.volume);
}).catch(err => {
    console.error("[-] Error starting camera: ", err);
    statusText.innerText = "Camera Access Blocked!";
    statusText.style.color = "red";
});
