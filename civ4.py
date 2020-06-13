import os
import uuid
import time
import json
import pathlib
from communication.procs import ThreadedProcessHandler
from recognition.actions.library import _mouse as mouse

proc = None

responses = {}

def location_center(loc):
    x = loc['left'] + loc['width']//2
    y = loc['top'] + loc['height']//2
    return x, y

def start():
    global proc
    root = str(pathlib.Path(__file__).absolute().parent)
    package_root = os.path.join(root, 'package')
    python = os.path.join(package_root, 'scripts', 'python.exe')
    main_dir = os.path.join(package_root, 'civ4')
    main = os.path.join(main_dir, 'main.py')
    proc = ThreadedProcessHandler(python, main, on_output=_on_message, cwd=main_dir)

def stop():
    proc.kill()
    print('c4stop')

def build(name):
    mouse.move(9999, 9999)
    resp = request({"type": "build initial", "asset": name})
    scene = resp.get('scene')
    down_arrow = resp['matches'].get('down arrow')
    if not scene:
        return
    if resp['matches'] and name in resp['matches']:
        center = location_center(resp['matches'][name])
        mouse.move(center[0], center[1])
        mouse.click()
    elif down_arrow:
        print(down_arrow)
        downx, downy = location_center(down_arrow)
        if scene == 'Start Turn':
            mouse.move(downx, downy - 15)
            mouse.click()
            time.sleep(3)
            resp = request({"type": "build", 'scene': scene, "asset": name})
            print('aik', resp)


def request(msg):
    msg_id = str(uuid.uuid4())
    msg_with_id = {'id': msg_id, **msg}
    msg_str = json.dumps(msg_with_id)
    proc.send_message(msg_str)
    resp = None
    start = time.time()
    while resp is None:
        if resp is None:
            time.sleep(0.01)
        resp = responses.get(msg_id)
    del responses[msg_id]
    return resp

def _on_message(msg_str):
    msg = json.loads(msg_str)
    responses[msg['id']] = msg['value']