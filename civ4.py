import os
import operator
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

def poll_scene():
    start_proc = proc
    req = {'type':2, 'match': 1 }
    while proc is start_proc:
        time.sleep(5)

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
    mouse.move(300, 300)
    asset_name = f'{direction} arrow'
    req = {"type": "match", "assets": [{'scene': 'Start Turn Build', 'assets': [asset_name]}, {'scene': 'City Build', 'assets': [asset_name]}]}
    resp = request(req)
    print(resp)
    if not resp:
        return
    x, y = location_center(resp['matches'][asset_name])
    if  resp['scene'] == 'Start Turn Build':
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
# {"type": "match", "assets": [{"scene": "Start Turn Build", "validation assets": ["up arrow", "down arrow"], "assets": ["settler"]}], "id": "abc"}

def build(asset):
    win_coords = window_coords()
    mouse.move(300, 300)
    validation_assets = ("up arrow", "down arrow")
    req = {"type": "match", "assets": []}
    for scene in ('Start Turn Build', 'City Build'):
        asset_collection = {'scene': scene, "validation assets": validation_assets, 'assets': [] if asset in validation_assets else [asset]}
        req['assets'].append(asset_collection)
    resp = request(req)
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
    req = {"type": "match", "assets": [{"scene": scene, "assets": [asset]}], 'window coords': win_coords}
    resp = request(req)
    if resp:
        click_location(resp['matches'][asset])
        return True
    return False

def scroll_and_click(scene, asset):
    for i in range(10):
        mouse.click()
        time.sleep(0.1)
        success = click_asset(scene, asset)
        if success:
            return

def select_custom_game_player_option(row_idx, col_idx):
    req = {"type": "match", "multiple": True, "assets": [{"scene": "Custom Game", "assets": ["top option selector"]}]}
    resp = request(req)
    if not resp:
        return
    win_coords = window_coords()
    sorted_matches = sorted(resp['matches']['top option selector'], key=operator.itemgetter('top', 'left'))
    rows = [[sorted_matches[0]]]
    heights = [sorted_matches[0]['top']]
    for match in sorted_matches[1:]:
        if match['top'] != rows[-1][-1]['top']:
            rows.append([])
        rows[-1].append(match)
    if row_idx == 0:
        win_coords = window_coords()
        is_first_row = len(rows[0]) == 4 and rows[0][-1]['left'] + 200 > win_coords['width']
        if is_first_row:
            if col_idx == 0:
                raise RuntimeError('Cannot select player')
            col_idx -= 1
    match = rows[row_idx][col_idx]
    click_location(match)

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

_SCENE_VALIDATION = {
    # 'Start Turn Build': ('up arrow', 'down arrow')
    # 'City Build': ('up arrow', 'down arrow')
}