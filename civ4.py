import os
import uuid
import time
import json
import pathlib
from communication.procs import ThreadedProcessHandler
from recognition.actions.library import _mouse as mouse, window

proc = None

responses = {}

def window_coords():
    x, y, w, h = window.active_window().coords
    return {'left': x, 'top': y, 'width': w, 'height': h}

def window_to_absolute_coords(x, y):
    win_coords = window.active_window().coords
    winx, winy = win_coords[0], win_coords[1]
    return winx + x, winy + y

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
    global proc
    proc.kill()
    proc = None

def scroll(direction, count=1):
    try:
        count = int(count)
    except (ValueError, TypeError):
        count = 1
    if count < 1:
        return
    asset_name = f'{direction} arrow'
    resp = request({"type": "build initial", "asset": asset_name})
    match = resp['matches'].get(asset_name)
    if not match:
        return
    x, y = location_center(match)
    if  resp['scene'] == 'Start Turn':
        y = y - 15 if direction == 'down' else y + 15
    mouse.move(x, y)
    for i in range(count):
        mouse.click()

def click_at(x, y):
    winx, winy, winw, winh = window.active_window().coords
    print(winw, winh)
    clickx = x + winx
    clicky = y + winy
    if x < 0:
        clickx += winw
    if y < 0:
        clicky += winh
    mouse.move(clickx, clicky)
    mouse.click()

def build(asset):
    win_coords = window_coords()
    mouse.move(300, 300)
    resp = request({"type": "build initial", "asset": asset, 'window_coords': win_coords})
    scene = resp.get('scene')
    if not scene:
        return
    down_arrow = resp['matches'].get('down arrow')
    if resp['matches'] and asset in resp['matches']:
        click_location(resp['matches'][asset])
    elif down_arrow:
        downx, downy = location_center(down_arrow)
        if scene == 'Start Turn':
            mouse.move(downx, downy - 15)
        elif scene == 'City Build':
            mouse.move(downx, downy)
        scroll_and_click(scene, asset)

def click_asset(scene, asset):
    win_coords = window_coords()
    resp = request({"type": "build", 'scene': scene, "asset": asset, 'window_coords': win_coords})
    if resp:
        click_location(resp)

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