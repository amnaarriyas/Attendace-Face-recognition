import cv2
import os
import time

# Create a directory for each person
person_name = "1"
os.makedirs(f"dataset/{person_name}", exist_ok=True)

# Initialize camera
cap = cv2.VideoCapture(0)

# Capture images with a delay
for img_num in range(20):
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('Capturing', frame)
    
    # Save the captured image
    cv2.imwrite(f"dataset/{person_name}/img_{img_num}.jpg", frame)
    
    # Wait for 2 seconds before capturing the next image
    time.sleep(2)
    
    # Press 'q' to quit capturing
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
