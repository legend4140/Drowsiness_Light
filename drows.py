import cv2
import dlib
from scipy.spatial import distance
import serial
import time
import pygame

# Connect to Arduino (replace 'COM4' with your port)
ser = serial.Serial('COM4', 9600)

# Initialize face detector and predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Function to calculate eye aspect ratio (EAR)
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Constants
EAR_THRESHOLD = 0.2  # Adjust this threshold according to your requirements
ALARM_DURATION_THRESHOLD = 2.5  # Duration in seconds for continuous alarm

# Variables for alarm state
ALARM_ON = False
ALARM_START_TIME = 0

# Initialize Pygame for alarm sound
pygame.init()
alarm_sound = pygame.mixer.Sound("alarm.wav")
alarm_playing = False

# Open webcam
cap = cv2.VideoCapture(0)

# Check if webcam opened successfully
if not cap.isOpened():
    print("Error: Unable to open webcam.")
    exit()

# Main loop
while True:
    # Read a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame from webcam.")
        break

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = detector(gray)

    # Initialize status
    status = "Not Drowsy"

    for face in faces:
        # Get facial landmarks
        landmarks = predictor(gray, face)
        left_eye = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)]
        right_eye = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)]

        # Calculate eye aspect ratio (EAR)
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        # Check if EAR is below threshold
        if ear < EAR_THRESHOLD:
            # Alarm Activation Logic
            if not ALARM_ON:
                ALARM_ON = True
                ALARM_START_TIME = time.time()
                print("Drowsiness Detected - Alarm Activated!")
                ser.write(b'drowsy\n')  # Send signal to Arduino

                # Play the alarm sound
                if not alarm_playing:
                    alarm_sound.play(-1)  # Loop the sound indefinitely
                    alarm_playing = True

            # Update status
            status = "Drowsy"

            # Blink lighting in red
            if int(time.time() * 2) % 2 == 0:
                cv2.putText(frame, "Drowsy", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            # Alarm Deactivation Logic
            if ALARM_ON and time.time() - ALARM_START_TIME >= ALARM_DURATION_THRESHOLD:
                ALARM_ON = False
                ser.write(b'not_drowsy\n')  # Send signal to Arduino
                if alarm_playing:
                    alarm_sound.stop()
                    alarm_playing = False

            # Update status
            status = "Not Drowsy"

            # Show lighting in green
            cv2.putText(frame, "Not Drowsy", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Continuous Alarm Logic
    if ALARM_ON and status == "Drowsy":
        if not alarm_playing:
            alarm_sound.play(-1)  # Start playing alarm sound if not already playing
            alarm_playing = True

    # Display the frame
    cv2.imshow("Frame", frame)

    # Check for 'q' key press to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()
