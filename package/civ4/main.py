import traceback
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

def handle_input(msg, scenes):
    monitor_num = 1
    if msg['type'] == 'build':
        scene = scenes[msg['scene']]
        ss, monitor, ss_bounds = images.screenshot(monitor_num=monitor_num, bounds_fn=scene.bounds)
        match = scene.find_match(ss, msg['asset'])
        if match:
            adjusted_match = adjust_match(match, monitor, ss_bounds)
            return adjusted_match
    elif msg['type'] == 'build initial':
        for scene_name in ['Start Turn', 'City Build']:
        # for scene_name in ['City Build']:
            scene = scenes[scene_name]
            ss, monitor, ss_bounds = images.screenshot(monitor_num=monitor_num, bounds_fn=scene.bounds)
            initial_match = scene.find_initial_match(ss, msg['asset'])
            debug(initial_match)
            adjusted_matches = {k: adjust_match(v, monitor, ss_bounds) for k, v in initial_match.items()}
            if adjusted_matches:
                return {'scene': scene_name, 'matches': adjusted_matches}
    return {}

def debug(msg):
    print(json.dumps({'debug': msg}))

def main():
    scenes = _scenes.load_scenes()
    while True:
        stdin = input()
        if not stdin:
            return
        else:
            msg = json.loads(stdin)
            try:
                resp = handle_input(msg, scenes)
            except Exception as e:
                err = traceback.format_exc()
                print(json.dumps({'id': msg['id'], 'error': err}))
            else:
                resp_str = json.dumps({'id': msg['id'], 'value': resp})
                print(resp_str)

main()

# {"type": "find matches", "scene": "Start Turn", "assets": ["settler"], "id": "abc"}
{"type": "build initial", "asset": "settler", "id": "abc"}