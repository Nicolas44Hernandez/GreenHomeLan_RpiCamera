"""
Video capture interface service
"""
import logging
import threading
import cv2
import queue


logger = logging.getLogger(__name__)
# TODO: get from stream
FPS = 10


class VideoCaptureInterface(threading.Thread):
    """Service class for video manager interface management"""

    fps: int
    capture: cv2.VideoCapture
    running: bool
    last_frame: queue.Queue

    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.last_frame = queue.Queue()
        self.running = True
        logger.info("Video manager interface started")

        self.reader_thread = threading.Thread(target=self.read_forever)
        self.reader_thread.daemon = True
        self.reader_thread.start()

    def read_forever(self):
        """Read frames as soon as they are available, keeping only most recent one"""

        while True:
            if self.running:
                ret, frame = self.capture.read()
                if not ret:
                    break
                if not self.last_frame.empty():
                    try:
                        # Discard previous frame
                        self.last_frame.get_nowait()
                    except queue.Empty:
                        pass
                self.last_frame.put(frame)
        # TODO: Raise exception if Error ?

    def get_last_frame(self):
        """Retrieve last captured frame"""
        try:
            frame = self.last_frame.get_nowait()
        except queue.Empty:
            return None
        return frame
