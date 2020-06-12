import cv2
import json
import numpy
from matplotlib import pyplot as plt
import mss
import time
import scenes as _scenes
import images
import mss

def adjust_match(match, img, cropped):
    # print(match)
    # print(img)
    # print(cropped)
    return {
        **match,
        'left': match['left'] + cropped['left'],
        'top': match['top'] + cropped['top'],
    }

def handle_input(inpt, scenes):
    msg = json.loads(inpt)
    if msg['type'] == 'find initial match':
        file_ss = cv2.imread('..\\assets\\start-turn-build.png', 0)
        s = time.time()
        ss = images.screenshot()
        scene = scenes[msg['scene']]
        asset = msg['asset']
        result = scene.find_initial_match(ss, asset)
        e = time.time()
        respond(msg['id'], result)
        # print(e-s)
        # for k, v in result.items():
        #     images.show_match(ss, v, title=k)
    elif msg['type'] == 'build initial':
        monitor_num = 1
        for scene_name in ['Start Turn']:
            scene = scenes[scene_name]
            bounds_fn = scene.screenshot_bounds
            # ss, monitor, ss_bounds = images.screenshot(monitor_num=monitor_num, bounds_fn=bounds_fn)
            ss, monitor, ss_bounds = images.screenshot_from_file('..\\assets\\startturnhighres.png', bounds_fn=bounds_fn)
            initial_match = scene.find_initial_match(ss, msg['asset'])
            adjusted_matches = {k: adjust_match(v, monitor, ss_bounds) for k, v in initial_match.items()}
            print(adjusted_matches[msg['asset']])
            ss_original, _, _ = images.screenshot_from_file('..\\assets\\startturnhighres.png')
            ssoverlay = images.overlay_rectangle(ss_original, adjusted_matches[msg['asset']])
            images.show_image(ssoverlay)
    else:
        raise ValueError(f'Unknown message type {msg["type"]}')

def respond(msg_id, response):
    resp_str = json.dumps({'id': msg_id, 'matches': response})
    print(resp_str)

def main():
    scenes = _scenes.load_scenes()
    while True:
        stdin = input()
        if not stdin:
            return
        else:
            handle_input(stdin, scenes)

main()

# {"type": "find matches", "scene": "Start Turn", "assets": ["settler"], "id": "abc"}
{"type": "build initial", "asset": "settler", "id": "abc"}