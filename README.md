# 2024IIOT_Team3 - Smart Parking System

The **Smart Parking System** is a real-time parking lot monitoring solution that uses a Raspberry Pi, YOLO object detection, and Blynk for remote parking space status updates. The project integrates a live video stream and provides the current occupancy status of parking spaces.

---

## Features

- **Real-Time Video Stream**: Live streaming of the parking lot using Flask and PiCamera.
- **Object Detection**: Detects vehicles using pretrained light-weight YOLOv11 model.
- **Blynk Integration**: Updates parking space statuses to the Blynk server for remote monitoring.
- **Parking Space Calibration**: Custom bounding boxes for each parking space ensure accurate detection.
- **IoU Calculation**: Identifies parking space occupancy using Intersection over Union (IoU).

---

## Requirements

1. **Hardware**:
   - Raspberry Pi 4 model B
   - Pi Camera 2
2. **Software**:
   - Python 3
   - Flask
   - OpenCV
   - [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
   - Picamera2

---

## Setup Instructions

### 1. Install Required Libraries

Install the required Python libraries using `pip`:

```bash
pip install flask opencv-python ultralytics numpy
```

### 2. Clone the Project

Clone this repository onto your Raspberry Pi:

```bash
git clone https://github.com/YanYuTu/2024IIOT_Team3.git
cd smart-parking-system
```
### 3. Configure Blynk Authentication

Update the BLYNK_AUTH variable in the smart_parking.py file with your Blynk authentication token:

```bash
BLYNK_AUTH = "Your_Blynk_Auth_Token"
```

### 4. Configure Calibrated Positions

Update the calibrated_positions list in the smart_parking.py file with bounding box coordinates for your parking spaces:

```bash
calibrated_positions = [
    (256, 294, 498, 424),
    (280, 180, 505, 300),
    (300, 77, 510, 189),
    (322, 1, 518, 95)
]
```
---

## Running the Application

1. Start the application by running the following command:
```bash
python smart_parking.py
```
2. Open a browser and navigate to http://<your-raspberry-pi-ip>:5000 to view the live stream.
3. Parking statuses are automatically updated to your Blynk dashboard.

---

## License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it.
