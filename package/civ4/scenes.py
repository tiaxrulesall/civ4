import time
import cv2
import mss
from matplotlib import pyplot as plt
import images

class Scene:
    pass

class StartTurnScene:

    def bounds(self, monitor):
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
            up_arrow_match = images.match_template_filename(img, self.asset_to_filename('up arrow')) 
            down_arrow_match = images.match_template_filename(img, self.asset_to_filename('down arrow')) 
            return {'up arrow': up_arrow_match, 'down arrow': down_arrow_match} if up_arrow_match and down_arrow_match else {} 

    def find_match(self, img, asset_name):
        return images.match_template_filename(img, self.asset_to_filename(asset_name))

    def asset_to_filename(self, asset_name: str):
        asset_name_dash = '-'.join(asset_name.split())
        return f'..\\assets\\{asset_name_dash}.png'

class CityBuildScene:

    def bounds(self, monitor):
        # anchored to bottom
        height = 130
        bottom = monitor['top'] + monitor['height']
        return {
            **monitor,
            'top': bottom - height,
            'height': height,
        }

    def find_initial_match(self, img, asset_name):
        asset_match = images.match_template_filename(img, self.asset_to_filename(asset_name))
        if asset_match:
            return {asset_name: asset_match}
        else:
            up_arrow_match = images.match_template_filename(img, self.asset_to_filename('up arrow')) 
            down_arrow_match = images.match_template_filename(img, self.asset_to_filename('down arrow')) 
            return {'up arrow': up_arrow_match, 'down arrow': down_arrow_match} if up_arrow_match and down_arrow_match else {} 

    def find_match(self, img, asset_name):
        return images.match_template_filename(img, self.asset_to_filename(asset_name))

    def asset_to_filename(self, asset_name: str):
        asset_name_dash = '-'.join(asset_name.split())
        return f'..\\assets\\city-{asset_name_dash}.png'

def load_scenes():
    return {
        'Start Turn': StartTurnScene(),
        'City Build': CityBuildScene(),
    }
