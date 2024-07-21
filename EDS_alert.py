import torch
import subprocess
import numpy as np
import cv2
from PIL import Image
import serial
from gpiozero import MotionSensor
import time
import os
import shutil  # Import for file operations

# Configure the serial connection
def send_sms(phone_number, message):
    ser.write(b'AT+CMGF=1\r')  # Set SMS to text mode
    time.sleep(1)
    ser.write(b'AT+CMGS="' + phone_number.encode() + b'"\r')
    time.sleep(1)
    ser.write(message.encode() + b'\r')
    time.sleep(1)
    ser.write(bytes([26]))  # ASCII code for Ctrl+Z
    time.sleep(3)
    print("SMS sent")

def capture_image():
    command = "sudo libcamera-jpeg -o test.jpg -t 1 --width 640 --height 480"
    try:
        subprocess.run(command, shell=True, check=True)
        print("Command executed successfully.")
        return 'test.jpg'  # Return the filename of the captured image
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None

def delete_image(file_path):
    try:
        os.remove(file_path)
        print(f"Image {file_path} deleted successfully.")
    except OSError as e:
        print(f"Error deleting file: {e}")

def delete_yolov5_run_directory():
    runs_dir = "runs/detect"  # Default directory where yolov5 saves results
    if os.path.exists(runs_dir):
        # Find the most recent run directory (last created/modified)
        latest_run_dir = max([os.path.join(runs_dir, d) for d in os.listdir(runs_dir)], key=os.path.getmtime)
        try:
            shutil.rmtree(latest_run_dir)
            print(f"Deleted yolov5 run directory: {latest_run_dir}")
        except OSError as e:
            print(f"Error deleting yolov5 run directory: {e}")
    else:
        print("No yolov5 runs directory found.")

def detection(image_path):    
    model = torch.hub.load("ultralytics/yolov5", "custom", path="best.pt")  # local model
    im1 = Image.open(image_path)

    # Inference
    results = model(im1, size=640)  # batch of images

    # Results
    results.print()
    results.save()  # Save the detection results (images will be saved in the runs directory)

    # Check if predictions are available for the first image
    if results.xyxy[0] is not None and len(results.xyxy[0]) > 0:
        predictions = results.xyxy[0]  # tensor containing predictions for im1
    
        # Convert predictions to a pandas DataFrame and print
        print(results.pandas().xyxy[0])  # im1 predictions in a tabular format
    
        output = []
        for prediction in predictions:
            x1, y1, x2, y2, confidence, cls = prediction.tolist()
            output.append({
                'bounding_box': [x1, y1, x2, y2],
                'confidence': confidence,
                'class': cls
            })
            # Print each class and confidence
            print(f'Class: {cls}, Confidence: {confidence:.2f}')

        # Example check for a specific condition (e.g., high confidence detection)
        for item in output:
            if item['confidence'] > 0.5:  # Adjust the threshold as needed
                print("High confidence detection:", item)
                if item['class'] == 0:  # Assuming '0' is the class for a leopard (adjust based on your model's classes)
                    send_sms("+9779869990884", "Leopard detected at the site no.1 in Dadagaun")
                    send_sms("+9779856022265", "Leopard detected at the site no.1 in Dadagaun")
                    send_sms("+9779847717958", "Leopard detected at the site no.1 in Dadagaun")
                    send_sms("+9779816698048", "Leopard detected at the site no.1 in Dadagaun")
                    send_sms("+9779856063692", "Leopard detected at the site no.1 in Dadagaun")
                    send_sms("+9779851210554", "Leopard detected at the site no.1 in Dadagaun")
    else:
        print("No objects detected.")
        delete_image(image_path)  # Delete the captured image if no objects are detected
        delete_yolov5_run_directory()  # Delete the yolov5 runs directory if no objects are detected

if __name__ == "__main__":
    # Initialize the SIM800L module
    ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

    # Initialize the PIR motion sensor
    pir = MotionSensor(23)

    while True:
        # Wait for motion
        pir.wait_for_motion()
        print("Motion Detected")

        # Capture an image
        image_path = capture_image()
        
        if image_path:
            # Perform object detection on the captured image
            detection(image_path)
            
        pir.wait_for_no_motion()
        print("Motion Stopped")
