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
    monitor_num = 1
    if msg['type'] == 'build':
        scene = scenes[msg['scene']]
        bounds_fn = scene.bounds
        ss, monitor, ss_bounds = images.screenshot(monitor_num=monitor_num, bounds_fn=bounds_fn)
        match = scene.find_match(ss, msg['asset'])
        images.show_image(ss)
        if match:
            adjusted_match = adjust_match(match, monitor, ss_bounds)
            respond(msg['id'], adjusted_match)
        return
    elif msg['type'] == 'build initial':
        for scene_name in ['Start Turn']:
            scene = scenes[scene_name]
            bounds_fn = scene.bounds
            ss, monitor, ss_bounds = images.screenshot(monitor_num=monitor_num, bounds_fn=bounds_fn)
            # ss, monitor, ss_bounds = images.screenshot_from_file('..\\assets\\startturnhighres.png', bounds_fn=bounds_fn)
            initial_match = scene.find_initial_match(ss, msg['asset'])
            adjusted_matches = {k: adjust_match(v, monitor, ss_bounds) for k, v in initial_match.items()}
            if adjusted_matches:
                respond(msg['id'], {'scene': scene_name, 'matches': adjusted_matches})
                return
        
    respond(msg['id'], {})
        # raise ValueError(f'Unknown message type {msg["type"]}')

def respond(msg_id, response):
    resp_str = json.dumps({'id': msg_id, 'value': response})
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