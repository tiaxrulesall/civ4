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
    scenes = _scenes.load_scenes()
    print(scenes)
    # img = cv2.imread('..\\assets\\start-turn-build.png',0)
    time.sleep(10)
    s = time.time()
    img = screenshot()
    gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    template = cv2.imread('..\\assets\\start-turn-settler.png', 0)
    w, h = template.shape[::-1]

    method = cv2.TM_CCOEFF_NORMED

    # Apply template Matching
    res = cv2.matchTemplate(gray_img, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    cv2.rectangle(gray_img,top_left, bottom_right, 255, 2)
    print(top_left)
    e = time.time()
    print(e-s)
    plt.subplot(121),plt.imshow(res, cmap = 'gray')
    plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(gray_img, cmap = 'gray')
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.suptitle(method)

    plt.show()

main()