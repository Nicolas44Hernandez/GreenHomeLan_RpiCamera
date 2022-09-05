import requests
import cv2
import random
import time
import base64

# Globals
TMP_PATH = "tmp.jpg"
FPS = 10
PICTURE_RATIO = 0.5
MAIN_URL = "http://127.0.0.1:4000"

# Unique camera id
def get_id():
    return "cam_"+str(random.random()).replace(".", "")

# Base64
def get_base_64(frame):
    cv2.imwrite(TMP_PATH, frame)
    with open(TMP_PATH, "rb") as jpg_file:
        data = base64.b64encode(jpg_file.read()).decode('utf-8')
        return data

# Send frame
def send_frame(cam_id, frame):
    frame_data = {"data":get_base_64(frame)}
    headers = {"cam_id":cam_id}
    try:
        print ("posting frame : "+ MAIN_URL)
        r = requests.post(MAIN_URL + "/frame_data", data=frame_data, headers=headers)
    except:
        print ("error posting")
        pass
        #print("[ERROR] Unable to send frame data")

# Main loop
def main():
    # Get video stream and unique cam id
    delay = 1./FPS
    cam = cv2.VideoCapture(0)
    cam_id = get_id()
    print("[INFO] Started cam", cam_id)

    # Loop until ECHAP or Q is pressed
    while(True):
        timer1 = time.time()
        # Grab and display frame
        ret, frame = cam.read()
        frame = cv2.resize(frame, None, fx=PICTURE_RATIO, fy=PICTURE_RATIO, interpolation=cv2.INTER_AREA)
        #cv2.imshow("Camera", frame)
        # Send frame
        send_frame(cam_id, frame)
        # Wait
        timer2 = time.time()
        ms_delay = max(1, int((delay-(timer2-timer1))*1000))
        k = cv2.waitKey(ms_delay) & 0xFF
        # Quit
        if k in [ord('q'), 27]:
            print("[INFO] Quitting")
            break

    # Release all
    cam.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    main()
