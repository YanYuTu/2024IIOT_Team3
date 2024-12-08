from ultralytics import YOLO
from flask import Flask, Response, render_template_string
from picamera2 import Picamera2
import cv2
import numpy as np

import sys
sys.path.append('./blynk-library-python')
import BlynkLib

# Modify blynk server authentication here
BLYNK_AUTH = ""

# Initialize the Flask app
app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Camera Stream</title>
</head>
<body>
    <h1>Pi Camera Vision</h1>
    <img src="{{ url_for('video_feed') }}" alt="Live Feed">
</body>
</html>
'''

def blynk_com():
    if curr_lots[0]:
        blynk.virtual_write(0, "Occupied")
        blynk.virtual_write(4, 1)
    else:
        blynk.virtual_write(0, "Free")
        blynk.virtual_write(4, 0)

    if curr_lots[1]:
        blynk.virtual_write(1, "Occupied")
        blynk.virtual_write(5, 1)
    else:
        blynk.virtual_write(1, "Free")
        blynk.virtual_write(5, 0)

    if curr_lots[2]:
        blynk.virtual_write(2, "Occupied")
        blynk.virtual_write(6, 1)
    else:
        blynk.virtual_write(2, "Free")
        blynk.virtual_write(6, 0)

    if curr_lots[3]:
        blynk.virtual_write(3, "Occupied")
        blynk.virtual_write(7, 1)
    else:
        blynk.virtual_write(3, "Free")
        blynk.virtual_write(7, 0)

def parking_lots_check():
    for i in range (4):
        curr_lots[i] = (prev_state[i] and curr_state[i]) or (prev_state[i] and not curr_state[i] and last_lots[i]) or (not prev_state[i] and curr_state[i] and last_lots[i])
    prev_state[:] = curr_state
    last_lots[:] = curr_lots
    curr_state[:] = [0] * len(curr_state)
    print("Current Parking lots status: ", curr_lots)

def calculate_iou(box1, box2):
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2

    # Intersection coordinates
    x1_inter = max(x1_1, x1_2)
    y1_inter = max(y1_1, y1_2)
    x2_inter = min(x2_1, x2_2)
    y2_inter = min(y2_1, y2_2)

    # No overlap
    if x1_inter >= x2_inter or y1_inter >= y2_inter:
        return 0

    # Intersection area
    intersection_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)

    # Area of each box
    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)

    # Union area
    union_area = box1_area + box2_area - intersection_area

    # IoU and convert to percentage
    iou = intersection_area / union_area
    return iou * 100

def draw_boxes(frame, results, model):
    # Draw bounding boxes around detected car objects (class 2)
    for box in results[0].boxes:
        cls = int(box.cls[0])
        if cls == 2:  # Class 2 represents car objects
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0]
            label = f"{model.names[cls]} {conf:.2f}"
            print(f"Detected - Top-left: ({x1}, {y1}), Bottom-right: ({x2}, {y2})")

            # Check overlap with predefined calibrated positions
            for i, calibrated_box in enumerate(calibrated_positions):
                overlap = calculate_iou((x1, y1, x2, y2), calibrated_box)
                print(f"Overlap with calibrated position {i+1}: {overlap:.2f}%")
                if overlap > 60:
                        curr_state[i] = 1

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_TRIPLEX, 0.5, 1)[0]
            label_x = x1
            label_y = y1 - 10 if y1 - 10 > 10 else y1 + 10
            cv2.rectangle(frame, (label_x, label_y - label_size[1] - 5),
                          (label_x + label_size[0] + 5, label_y + 5),
                          (255, 255, 255), -1)
            cv2.putText(frame, label, (label_x, label_y), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 0), 1)
    return frame

def generate_frames(picam2, model):
    while True:
        blynk.run()

        # Capture frame from the camera
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Perform object detection on the frame
        results = model(frame)

        # Draw bounding boxes on the frame
        frame = draw_boxes(frame, results, model)

	# Check parking lots status
        parking_lots_check()

        # Upload data to Blynk Server
        blynk_com()

        # Convert the frame to JPEG and send it for live streaming
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    # Return the video feed in a format suitable for live streaming
    return Response(generate_frames(picam2, model),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Load the YOLO model for object detection
    model = YOLO('yolo11n_ncnn_model')

    # Initialize the camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration())
    picam2.start()

    # Calibrated positions for the parking lots (bounding box coordinates)
    calibrated_positions = [
        (256, 294, 498, 424),
        (280, 180, 505, 300),
        (300, 77, 510, 189),
        (322, 1, 518, 95)
    ]

    # Initial and current state of each parking lot (0 means empty, 1 means occupied)
    prev_state = [0, 0, 0, 0]
    curr_state = [0, 0, 0, 0]
    last_lots  = [0, 0, 0, 0]
    curr_lots  = [0, 0, 0, 0]

    # Initialize blynk
    blynk = BlynkLib.Blynk(BLYNK_AUTH)

    app.run(host='0.0.0.0', port=5000)
