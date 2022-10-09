import cv2
import win32api, win32con, win32ui, win32gui
from mss import mss
import numpy as np
import threading
import time
import win32api, win32con
import clr
# change this to wherever your built DLL is
clr.AddReference(r'C:ClassLibrary1.dll')
from ClassLibrary1 import Class1
ud_mouse = Class1()

class Grabber:
    def __init__(self) -> None:
        # self.lower = np.array([139, 96, 129], np.uint8)
        # self.upper = np.array([169, 255, 255], np.uint8)
        self.lower = np.array([139, 95, 154], np.uint8)
        self.upper = np.array([153, 255, 255], np.uint8)
    def find_dimensions(self, box_size):
        """Calculates constants required for the bot."""
        self.box_size = box_size
        self.box_middle = int(self.box_size / 2)
        top = int(((799 / 2) - (self.box_size / 2)))
        left = int(((1366 / 2) - (self.box_size / 2)))
        self.dimensions = {'top': top, 'left': left, 'width': self.box_size, 'height': self.box_size}
    def capture_frame(self):
        with mss() as sct:
            return np.array(sct.grab(self.dimensions))
    def process_frame(self, frame):
        """Performs operations on a frame to improve contour detection."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        processed = cv2.inRange(hsv, self.lower, self.upper)
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, np.ones((10, 10), np.uint8))
        dilatation_size = 2
        dilation_shape = cv2.MORPH_RECT
        element = cv2.getStructuringElement(dilation_shape, (2 * dilatation_size + 1, 2 * dilatation_size + 1),
                                    (dilatation_size, dilatation_size))
        processed = cv2.dilate(processed, element)
        processed = cv2.blur(processed, (8, 8))
        return processed
    def detect_contours(self, frame, minimum_size):
        """Returns contours larger then a specified size in a frame."""
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_contours = []
        if len(contours) != 0:
            for i in contours:
                if ud_mouse.Check(cv2.contourArea(i), minimum_size):
                # if cv2.contourArea(i) > minimum_size:
                    large_contours.append(i)
        return large_contours
    def compute_centroid(self, contour):
        """Returns x- and y- coordinates of the center of the largest contour."""
        c = max(contour, key=cv2.contourArea)
        rectangle = np.int0(cv2.boxPoints(cv2.minAreaRect(c)))
        new_box = []
        for point in rectangle:
            point_x = point[0]
            point_y = point[1]
            new_box.append([round(point_x, -1), round(point_y, -1)])
        M = cv2.moments(np.array(new_box))
        if M['m00']:
            center_x = (M['m10'] / M['m00'])
            center_y = (M['m01'] / M['m00'])
            x = -(self.box_middle - center_x)
            y = -(self.box_middle - center_y)
            return [], x, y
    def is_activated(self, key_code) -> bool:
        return ud_mouse.is_activated(key_code)
    def move_mouse(self, x, y):

        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(x), int(y))

    def _move_mouse(self, x, y):
        #                   x       y       box_size            multiply     y_diff      smoothing
        ud_mouse.move_mouse(int(x), int(y), self.box_size, 0.1, 0.9, 1)
