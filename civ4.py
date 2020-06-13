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

def click_location(loc):
    x, y = location_center(loc)
    mouse.move(x, y)
    mouse.click()

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

def build(asset):
    mouse.move(300, 300)
    resp = request({"type": "build initial", "asset": asset})
    scene = resp.get('scene')
    down_arrow = resp['matches'].get('down arrow')
    if not scene:
        return
    if resp['matches'] and asset in resp['matches']:
        click_location(resp['matches'][asset])
    elif down_arrow:
        downx, downy = location_center(down_arrow)
        if scene == 'Start Turn':
            mouse.move(downx, downy - 15)
        elif scene == 'City Build':
            mouse.move(downx, downy)
        scroll_and_click(scene, asset)

def scroll_and_click(scene, asset):
    for i in range(10):
        mouse.click()
        time.sleep(0.1)
        resp = request({"type": "build", 'scene': scene, "asset": asset})
        if resp:
            click_location(resp)
            return

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
    if 'error' in resp:
        raise RuntimeError(resp['error'])
    return resp['value']

def _on_message(msg_str):
    msg = json.loads(msg_str)
    if 'debug' in msg:
        print(msg['debug'])
    else:
        responses[msg['id']] = msg