import cv2
import json
import numpy
from matplotlib import pyplot as plt
import mss
import time
import scenes as _scenes
import images

def handle_input(inpt, scenes):
    msg = json.loads(inpt)
    if msg['type'] == 'find initial match':
        file_ss = cv2.imread('..\\assets\\start-turn-build.png', 0)
        s = time.time()
        ss = cv2.cvtColor(images.screenshot(), cv2.COLOR_RGB2GRAY)
        scene = scenes[msg['scene']]
        asset = msg['asset']
        result = scene.find_initial_match(ss, asset)
        e = time.time()
        respond(msg['id'], result)
        # print(e-s)
        # for k, v in result.items():
        #     images.show_match(ss, v, title=k)
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