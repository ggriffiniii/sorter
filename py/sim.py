import os
import sorterlib
import sys

IMG_DIR = sys.argv[1]

tubes = []

class Tube(object):
    def __init__(self, color):
        self.color = color
        self.count = 0

    def __str__(self):
        return f'Tube({self.color}, count={self.count})'

for filename in sorted(os.listdir(IMG_DIR)):
    filename = os.path.join(IMG_DIR, filename)
    with open(filename, 'rb') as f:
        img_data = f.read()
    (bead_color, _) = sorterlib.bead_color(img_data)
    (best_tube, dist) = min(((tube, sorterlib.rgb_dist(bead_color, tube.color)) for tube in tubes), key=lambda pair: pair[1], default=(None, 2**31))
    if dist < 50 or len(tubes) == 30:
        print(f'{filename}: bead_color: {bead_color}: {dist} from {best_tube} assigning')
        best_tube.count += 1
    else:
        print(f'{filename}: bead_color: {bead_color}: {dist} from {best_tube} allocating new tube')
        tubes.append(Tube(bead_color))
