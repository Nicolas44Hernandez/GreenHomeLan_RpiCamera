import cv2

cap = cv2.VideoCapture(0)

cap.set(3, 640)
cap.set(4, 480)


for i in range(10):
    ret, frame = cap.read()
    if ret:
        name = f"frame{i}.png"
        print("{name}")
        cv2.imwrite(name, frame)


cap.release()
cv2.destroyAllWindows()
