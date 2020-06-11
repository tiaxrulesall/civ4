import time
import numpy
import cv2
import mss
from matplotlib import pyplot as plt

asset_images = {}

def get_asset_image(filename):
    if filename not in asset_images:
        gray_image = cv2.imread(filename, 0)
        if gray_image is None:
            raise RuntimeError(f"Can't read {filename}")
        asset_images[filename] = gray_image
    return asset_images[filename]

def match_template_filename(img, template_filename):
    return match_template(img, get_asset_image(template_filename))

def match_template(img, template):
    width, height = template.shape[::-1]
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < 0.95:
        return None
    left, top = max_loc
    bottom, right = top + height, left + width
    return {
        'top': top,
        'left': left,
        'bottom': bottom,
        'right': right,
    }

def show_match(img, match, title=None):
    top_left = match['left'], match['top']
    bottom_right = match['right'], match['bottom']
    img = img.copy()
    cv2.rectangle(img, top_left, bottom_right, 255, 2)
    plt.imshow(img, cmap = 'gray')
    if title is not None:
        plt.title(title), plt.xticks([]), plt.yticks([])
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show()    

def screenshot():
    with mss.mss() as sct:
        # Get a screenshot of the 1st monitor
        sct_img = sct.grab(sct.monitors[1])
        return numpy.array(sct_img)