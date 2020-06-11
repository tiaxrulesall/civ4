import time
import cv2
from matplotlib import pyplot as plt
import images

class StartTurnScene:

    # def find_matches(self, img, asset_names):
    #     up_arrow_match = images.match_template_filename(img, self.asset_to_filename('up arrow'))
    #     down_arrow_match = images.match_template_filename(img, self.asset_to_filename('down arrow'))
    #     if not (up_arrow_match or down_arrow_match):
    #         return None
    #     result = {
    #         'up arrow': up_arrow_match,
    #         'down arrow': down_arrow_match,
    #     }
    #     for name in asset_names:
    #         if name not in result:
    #             result[name] = images.match_template_filename(img, self.asset_to_filename(name))
    #     return result

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
    return {'Start Turn': StartTurnScene()}
