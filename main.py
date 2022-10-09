from grabber import *
import time

grabber = Grabber()
grabber.find_dimensions(160)

print(f'box_size = {grabber.box_size}')

while True:
    last_time = time.time()
    og = grabber.capture_frame()
    frame = grabber.process_frame(og)
    contours = grabber.detect_contours(frame, 800)
    if contours:
        rec, x, y = grabber.compute_centroid(contours)
        if grabber.is_activated(0x06):
          grabber.move_mouse(x, y)


        cv2.drawContours(og, contours, -1, (0, 0, 0), 4)
        if rec:
            cv2.drawContours(og, rec, -1, (0, 255, 0), 4)
    cv2.imshow('frame', og)
    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        exit()
