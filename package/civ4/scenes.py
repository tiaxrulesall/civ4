class Scene:

    def __init__(self, name: str, images):
        self.name = name
        self.images = images
        self.required_images = [k for k, v in images.items() if v.get('required')]
        print(self.required_images)

    
    

def turn_start_build_scene():
    images = {
        'up arrow': {'images': ['start-turn-up-arrow.png'], 'required': True},
        'down arrow': {'images': ['start-turn-down-arrow.png'], 'required': True},
        'settler': {'images': ['start-turn-settler.png']}
    }
    return Scene('Turn Start Build', images)

def load_scenes():
    _scenes = [
        turn_start_build_scene()
    ]
    return {s.name: s for s in _scenes}