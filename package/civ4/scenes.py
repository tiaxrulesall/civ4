import time
import cv2
import mss
from matplotlib import pyplot as plt
import images

class Scene:
    pass

class StartTurnScene:

    def screenshot_bounds(self, monitor):
        # anchored to top right
        width = 500
        height = 560
        top = 50
        return {
            'left': monitor['width'] - width,
            'top': monitor['top'] + top,
            'width': width,
            'height': height,
        }

    def find_initial_match(self, img, asset_name):
        asset_match = images.match_template_filename(img, self.asset_to_filename(asset_name))
        if asset_match:
            return {asset_name: asset_match}
        else:
            return {
                'up arrow': images.match_template_filename(img, self.asset_to_filename('up arrow')),
                'down arrow': images.match_template_filename(img, self.asset_to_filename('down arrow')),
            }

    def asset_to_filename(self, asset_name: str):
        asset_name_dash = '-'.join(asset_name.split())
        return f'..\\assets\\start-turn-{asset_name_dash}.png'

class CityBuildScene:

    def screenshot_bounds(self):
        pass

    def find_initial_match(self, img, asset_name):
        asset_match = images.match_template_filename(img, self.asset_to_filename(asset_name))
        if asset_match:
            return {asset_name: asset_match}
        else:
            return {
            'up arrow': images.match_template_filename(img, self.asset_to_filename('up arrow')),
            'down arrow': images.match_template_filename(img, self.asset_to_filename('down arrow')),
        }

    def asset_to_filename(self, asset_name: str):
        asset_name_dash = '-'.join(asset_name.split())
        return f'..\\assets\\start-turn-{asset_name_dash}.png'

def load_scenes():
    return {
        'Start Turn': StartTurnScene(),
        'City Build': CityBuildScene(),
    }
