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
    x = (loc['right'] + loc['left']) // 2
    y = (loc['bottom'] + loc['top']) // 2
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

def click_asset(name):
    mouse.move(9999, 9999)
    resp = request({"type": "find initial match", "scene": "Start Turn", "asset": name})
    if resp['matches'] and resp['matches'][name]:
        center = location_center(resp['matches'][name])
        mouse.move(center[0], center[1])
        mouse.click()
    print(resp)

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
    responses[msg['id']] = msg