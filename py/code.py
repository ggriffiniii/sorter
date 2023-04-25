MAX_TUBES = 30
COLOR_DIST_THRESHOLD = 40

tubes = []
class Tube:
  def __init__(self, idx, color):
    self.idx = idx
    self.color = color
    self.count = 1

  def row_idx(self):
    r = self.idx % 15
    return (self.idx // 15) << 1 | (r & 1)

  def slice_idx(self):
    return self.idx % 15

def best_tube_for_color(color):
  return min(
      (
          (tube, sorterlib.rgb_dist(color, tube.color))
          for tube
          in tubes
      ),
      key=lambda pair: pair[1],
      default=(None, 2**31)
  )

def loop():
  while True:
    run()

def run():
  // pickup bead
  // take picture
  bead_color = sorterlib.bead_color(img)
  (best_tube, color_dist) = best_tube_for_color(bead_color)
  if color_dist < COLOR_DIST_THRESHOLD or len(tubes) == MAX_TUBES:
    best_tube.count += 1
    // move chute servo to best_tube.slice_idx()
    // move hopper servo to best_tube.row_idx()
  else:
    tubes.append(Tube(len(tubes), bead_color))



if __name__ == "__main__":
  loop()

 
 
