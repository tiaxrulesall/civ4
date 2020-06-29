import traceback
import cv2
import json
import numpy
import os.path
from matplotlib import pyplot as plt
import mss
import time
import scenes as _scenes
import images
import regions
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

def handle_input(msg):
    monitor_num = 1
    if msg['type'] == 'match':
        match_fn = images.match_template if not msg.get('multiple') else images.match_template_multiple
        for asset_collection in msg['assets']:
            matches = {}
            bounds_fn = get_bounds_fn(asset_collection['scene'])
            if 'screenshot' in msg:
                file_path = os.path.join('..', 'assets', msg['screenshot'])
                ss, monitor, ss_bounds = images.screenshot_from_file(filename=file_path, bounds_fn=bounds_fn)
            else:
                ss, monitor, ss_bounds = images.screenshot(monitor_num=monitor_num, bounds_fn=bounds_fn)
            validation_assets = asset_collection.get('validation assets')
            if validation_assets:
                for asset in validation_assets:
                    asset_path = get_asset_path(asset_collection['scene'], asset)
                    template = images.get_asset_image(asset_path)
                    match = match_fn(ss, template)
                    if match:
                        matches[asset] = match
            if not matches and validation_assets:
                continue
            for asset in asset_collection['assets']:
                asset_path = get_asset_path(asset_collection['scene'], asset)
                template = images.get_asset_image(asset_path)
                match = match_fn(ss, template)
                if match:
                    matches[asset] = match
            if matches:
                adjusted_matches = {}
                for asset, match in matches.items():
                    adjusted_matches[asset] = [adjust_match(x, monitor, ss_bounds) for x in match] if isinstance(match, list) else adjust_match(match, monitor, ss_bounds)
                return {'scene': asset_collection['scene'], 'matches': adjusted_matches}
    elif msg['type'] == 'state':
        pass
    return {}

def debug(msg):
    print(json.dumps({'debug': msg}))

def get_bounds_fn(scene: str):
    return {
        'City Build': regions.bottom,
        'Promotions': regions.bottom,
        'Start Turn Build': regions.start_turn_menu,
        'Start Turn Research': regions.start_turn_menu,
    }.get(scene, lambda x: x.copy())

def get_asset_path(scene, asset_name):
    root = os.path.join('..', 'assets')
    asset_folder = {
        'City Build': 'city-build',
        'Custom Game': 'custom-game',
        'Promotions': 'promotions',
        'Start Turn Build': 'start-turn-build',
    }[scene]
    asset_file_name = f"{'-'.join(asset_name.split())}.png"
    return os.path.join(root, asset_folder, asset_file_name)


def main():
    while True:
        stdin = input()
        if not stdin:
            return
        else:
            msg = json.loads(stdin)
            try:
                resp = handle_input(msg)
            except Exception as e:
                err = traceback.format_exc()
                print(json.dumps({'id': msg['id'], 'error': err}))
            else:
                resp_str = json.dumps({'id': msg['id'], 'value': resp})
                print(resp_str)

main()

# {"type": "find matches", "scene": "Start Turn", "assets": ["settler"], "id": "abc"}
{"type": "build initial", "asset": "settler", "id": "abc"}
{"type": "match", "screenshot": "startturnhighres.png", "assets": [{"scene": "Start Turn Build", "validation assets": ["up arrow", "down arrow"], "assets": ["settler"]}], "id": "abc"}
{"type": "match", "assets": [{"scene": "Start Turn Build", "validation assets": ["up arrow", "down arrow"], "assets": ["settler"]}], "id": "abc"}
{"type": "match", "screenshot": "custom-game-multi.png", "multiple": true, "assets": [{"scene": "Custom Game", "assets": ["top option selector"]}], "id": "abc"}