import cv2

cap = cv2.VideoCapture(0)  
if not cap.isOpened():
    print("camera not open")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("frame not loading")
        break

    cv2.imshow('Camera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # q
        break

cap.release()
cv2.destroyAllWindows()
