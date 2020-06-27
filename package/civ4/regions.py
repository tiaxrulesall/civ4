def start_turn_menu(edges):
    # anchored to top right
    width = 500
    height = 560
    top = 50
    return {
        'left': edges['width'] - width,
        'top': edges['top'] + top,
        'width': width,
        'height': height,
    }

def bottom(monitor):
    # anchored to bottom
    height = 130
    bottom = monitor['top'] + monitor['height']
    return {
        **monitor,
        'top': bottom - height,
        'height': height,
    }