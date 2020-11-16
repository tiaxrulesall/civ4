import os
import functools
import threading
import operator
import uuid
import time
import json
from types import SimpleNamespace
import pathlib
from communication.procs import ThreadedProcessHandler
from recognition.actions.library import _mouse as mouse, window, stdlib, _keyboard as keyboard

def proc():
    return stdlib.namespace['state'].civ4['proc']

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

def poll_scene(start_proc):
    custom_game = {'scene': 'Custom Game', 'validation assets': ['pane slider']}
    req = {
        'type': 'match',
        'scenes': [
            custom_game
        ]
    }
    while True:
        try:
            current_proc = proc()
        except AttributeError:
            return
        if current_proc is not start_proc:
            return
        resp = request(req)
        if resp:
            stdlib.namespace['state'].civ4.update({'scene': resp['scene'], 'matches': resp['matches']})
        else:
            stdlib.namespace['state'].civ4.update({'scene': None, 'matches': []})
        # print(stdlib.namespace['state'].civ4)
        time.sleep(2)

def start():
    root = str(pathlib.Path(__file__).absolute().parent)
    package_root = os.path.join(root, 'package')
    python = os.path.join(package_root, 'scripts', 'python.exe')
    main_dir = os.path.join(package_root, 'civ4')
    main = os.path.join(main_dir, 'main.py')
    proc = ThreadedProcessHandler(python, main, on_output=_on_message, cwd=main_dir)
    stdlib.namespace['state'].civ4 = {'proc': proc, 'scene': None, 'matches': []}
    threading.Thread(target=poll_scene, args=(proc,)).start()

def stop():
    proc().kill()
    del stdlib.namespace['state'].civ4

def scene_match_skeleton(scene):
    if scene == 'Custom Game':
        validation_assets = ['pane slider']
    elif scene == 'Start Turn Build':
        validation_assets = ['up arrow', 'down arrow', 'examine city']
    elif scene == 'City Build':
        validation_assets = ['up arrow', 'down arrow']
    else:
        validation_assets = []
    return {'scene': scene, 'validation assets': validation_assets, 'assets': []}

def get_match_from_response(asset, resp):
    try:
        return resp['matches'][asset]
    except KeyError:
        pass

def add_ai():
    match = custom_game_scroll('down', 'top', check_fn=check_ai, count=18)
    if match:
        click_location(match)
        for i in range(2):
            keyboard.KeyPress.from_space_delimited_string('down').send()
        keyboard.KeyPress.from_space_delimited_string('up').send()
        keyboard.KeyPress.from_space_delimited_string('enter').send()

def check_ai():
    req = {"type": "match", "scenes": [{**scene_match_skeleton('Custom Game'), 'assets': ['open', 'closed']}]}
    resp = request(req)
    return get_match_from_response('open', resp) or get_match_from_response('closed', resp)

def custom_game_scroll(direction, menu, check_fn=lambda: False, count=1):
    check_result = check_fn()
    if check_result:
        return check_result
    count = parse_number(count)
    x, y = custom_game_scroll_location(direction, menu)
    mouse.move(x, y)
    for i in range(count):
        mouse.click()
        time.sleep(0.1)
        check_result = check_fn()
        if check_result:
            return check_result


def custom_game_scroll_location(direction, menu):
    asset_name = f'{direction} arrow'
    req = {"type": "match", 'multiple': True, "scenes": [{**scene_match_skeleton('Custom Game'), 'assets': [asset_name]}]}
    resp = request(req)
    if not resp:
        return
    matches = resp['matches'][asset_name]
    if len(matches) == 2:
        loc = matches[0] if menu == 'top' else matches[1]
    x, y = location_center(loc)
    y_adjustment = 0
    if menu == 'bottom':
        y_adjustment = 12 if direction == 'up' else -12
    return x, y + y_adjustment

def scroll(direction, count=1):
    count = parse_number(count)
    try:
        count = int(count)
    except (ValueError, TypeError):
        count = 1
    if count < 1:
        return
    asset_name = f'{direction} arrow'
    req = {"type": "match", "scenes": [{'scene': 'Start Turn Build', 'assets': [asset_name]}, {'scene': 'City Build', 'assets': [asset_name]}]}
    resp = request(req)
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
    clickx = x + winx
    clicky = y + winy
    if x < 0:
        clickx += winw
    if y < 0:
        clicky += winh
    mouse.move(clickx, clicky)
    mouse.click()

def focus_unit(unit_asset, from_num, to_num, do_select):
    req = {"type": "match", 'multiple': True, "scenes": [{**scene_match_skeleton('Unit Selection'), 'assets': [unit_asset]}]}
    resp = request(req)
    if not resp['matches']:
        return
    locs = [location_center(x) for x in _normalize_rows(resp['matches'][unit_asset])]
    shift_pressed = False
    if do_select:
        keyboard.KeyPress.from_space_delimited_string('shift_hold').send()
        shift_pressed = True
    from_idx = _num_to_index(from_num, locs)
    to_idx = _num_to_index(to_num, locs)
    if to_idx is not None:
        from_idx, to_idx = sorted((from_idx, to_idx))
    else:
        to_idx = from_idx + 1
    click_at(*locs[from_idx])
    time.sleep(0.1)
    for x, y in locs[from_idx + 1: to_idx]:
        if not shift_pressed:
            keyboard.KeyPress.from_space_delimited_string('shift_hold').send()
            shift_pressed = True
        time.sleep(0.1)
        click_at(x, y)
        time.sleep(0.1)
    if shift_pressed:
        time.sleep(0.1)
        keyboard.KeyPress.from_space_delimited_string('shift_release').send()

def _normalize_rows(locations):
    return sorted(locations, key=functools.cmp_to_key(location_comparison))

def _num_to_index(num, collection):
    if not num:
        return num
    if num < 0:
        return len(collection) + num
    return num - 1

# {"type": "match", "assets": [{"scene": "Start Turn Build", "validation assets": ["up arrow", "down arrow"], "assets": ["settler"]}], "id": "abc"}

def build(asset):
    win_coords = window_coords()
    req = {"type": "match", "scenes": []}
    for scene in ('Start Turn Build', 'City Build'):
        asset_collection = scene_match_skeleton(scene)
        if asset not in asset_collection['validation assets']:
            asset_collection['assets'].append(asset)
        req['scenes'].append(asset_collection)
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

def custom_game_setting(num):
    req = {'type': 'match', 'scenes': [{**scene_match_skeleton('Custom Game'), 'assets': ['settings-selector']}], 'multiple': True}
    resp = request(req)
    matches = resp['matches']['settings-selector']
    idx = _num_to_index(num, matches)
    click_location(matches[idx])

def click_asset(scene, asset):
    loc = find_asset(scene, asset)
    if loc:
        click_location(loc)
        return True
    return False

def find_asset(scene, asset):
    win_coords = window_coords()
    req = {"type": "match", "scenes": [{"scene": scene, "assets": [asset]}], 'window coords': win_coords}
    resp = request(req)
    if resp:
        return resp['matches'][asset]

def scroll_and_click(scene, asset):
    for i in range(10):
        mouse.click()
        time.sleep(0.1)
        success = click_asset(scene, asset)
        if success:
            return

def select_custom_game_player_option(row_idx, col_idx):
    req = {"type": "match", "multiple": True, "scenes": [{**scene_match_skeleton('Custom Game'), "assets": ["top option selector"]}]}
    resp = request(req)
    if not resp:
        return
    win_coords = window_coords()
    matches = resp['matches']['top option selector']
    rows = [[matches[0]]]
    heights = [matches[0]['top']]
    for match in matches[1:]:
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

def parse_number(n, default=1):
    try:
        return int(n)
    except (ValueError, TypeError):
        return default

def request(msg):
    msg_id = str(uuid.uuid4())
    msg_with_id = {'id': msg_id, **msg}
    msg_str = json.dumps(msg_with_id)
    proc().send_message(msg_str)
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

def location_comparison(loc_a, loc_b):
    acmp = loc_a['top'], loc_a['left']
    bcmp = loc_b['top'], loc_b['left']
    threshold = 5
    if abs(acmp[0] - bcmp[0]) < threshold:
        acmp, bcmp = acmp[1], bcmp[1]
    if acmp == bcmp:
        return 0
    return 1 if acmp > bcmp else -1