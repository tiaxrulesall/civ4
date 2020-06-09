import cv2
import numpy
from matplotlib import pyplot as plt
import mss
import time
import scenes as _scenes

    

def screenshot():
    with mss.mss() as sct:
        # Get a screenshot of the 1st monitor
        sct_img = sct.grab(sct.monitors[1])
        return numpy.array(sct_img)

def main():
    # time.sleep(10)
    s = time.time()
    img = screenshot()
    gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray_img = cv2.imread('..\\assets\\start-turn-build.png', 0)
    template = cv2.imread('..\\assets\\start-turn-settler.png', 0)
    scenes = _scenes.load_scenes()
    print(scenes['start turn'].query(gray_img,'settler'))

main()