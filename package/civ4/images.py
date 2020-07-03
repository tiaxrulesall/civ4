import time
import operator
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
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val > 0.9:
        left, top = max_loc
        width, height = template.shape[::-1]
        return {
            'top': top,
            'left': left,
            'height': height,
            'width': width,
        }

def overlay_rectangle(img, rectangle):
    top_left = rectangle['left'], rectangle['top']
    bottom_right = rectangle['left'] + rectangle['width'], rectangle['top'] + rectangle['height']
    img = img.copy()
    cv2.rectangle(img, top_left, bottom_right, 255, 2)
    return img

def show_image(img, title=None):
    plt.imshow(img, cmap = 'gray')
    if title is not None:
        plt.title(title), plt.xticks([]), plt.yticks([])
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show()    

def screenshot(monitor_num=1, bounds_fn=None):
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_num]
        ss_bounds = bounds_fn(monitor) if bounds_fn else monitor
        # Get a screenshot of the 1st monitor
        sct_img = sct.grab(ss_bounds)
        return cv2.cvtColor(numpy.array(sct_img), cv2.COLOR_RGB2GRAY), monitor, ss_bounds

def screenshot_from_file(filename, bounds_fn=None):
    img = cv2.imread(filename, 0)
    width, height = img.shape[::-1]
    bounds = {'left': 0, 'top': 0, 'width': width, 'height': height}
    ss_bounds = bounds_fn(bounds) if bounds_fn else bounds
    crop_img = img[ss_bounds['top']: ss_bounds['top'] + ss_bounds['height'], ss_bounds['left']: ss_bounds['left'] + ss_bounds['width']]
    return crop_img, bounds, ss_bounds

def match_template_multiple(img, template):
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    matches = []
    # fake out max_val for first run through loop
    max_val = 1
    while max_val > threshold:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > threshold:
            left, top = max_loc
            width, height = template.shape[::-1]
            matches.append({'top': top, 'left': left, 'height': height, 'width': width})
            res[max_loc[1]-height//2:max_loc[1]+height//2+1, max_loc[0]-width//2:max_loc[0]+width//2+1] = 0   
            img = cv2.rectangle(img, (max_loc[0],max_loc[1]), (max_loc[0]+width+1, max_loc[1]+height+1), (0,255,0) )
    return sorted(matches, key=operator.itemgetter('top', 'left'))
