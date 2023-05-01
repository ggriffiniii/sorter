try:
  import itertools
except ImportError:
  import adafruit_itertools as itertools
import math
from collections import namedtuple

IMG_WIDTH = 40
IMG_HEIGHT = 30
IMG_SIZE = IMG_WIDTH * IMG_HEIGHT

RGB = namedtuple("RGB", "r g b")

sqrt = math.sqrt

def rgb_dist(a, b):
  rmean = (a.r + b.r) // 2
  r = a.r - b.r
  g = a.g - b.g
  b = a.b - b.b
  return int(sqrt(
      (((512+rmean)*r*r)>>8)
      +
      4*g*g
      +
      (((767-rmean)*b*b)>>8))
  )

def rgb_mean(rgb_iterable):
  count = 0
  sum_rgb = RGB(0, 0, 0)
  for rgb in rgb_iterable:
    count += 1
    sum_rgb = RGB(
        sum_rgb.r + (rgb.r * rgb.r),
        sum_rgb.g + (rgb.g * rgb.g),
        sum_rgb.b + (rgb.b * rgb.b),
    )

  if count == 0:
    return RGB(0,0,0)

  return RGB(
    int(sqrt(sum_rgb.r // count)),
    int(sqrt(sum_rgb.g // count)),
    int(sqrt(sum_rgb.b // count)),
  )

BEAD_ARC_LEN = 19

def bead_arc(start_pixel):
  start_x = start_pixel % IMG_WIDTH
  start_y = start_pixel / IMG_WIDTH
  assert start_x < IMG_WIDTH-7
  assert start_y > 7

  idx = start_pixel
  yield idx
  for _ in range(5):
    idx -= IMG_WIDTH
    yield idx

  idx -= IMG_WIDTH - 1
  yield idx

  for _ in range(6):
    idx += 1
    yield idx

  idx += IMG_WIDTH + 1
  yield idx

  for _ in range(5):
    idx += IMG_WIDTH
    yield idx

def _rgb_for_pixel(img, pixel_idx):
  assert pixel_idx < IMG_SIZE
  idx = pixel_idx * 2
  r5 = img[idx] >> 3
  g6 = ((img[idx] << 3) | (img[idx+1] >> 5)) & 0b111111
  b5 = (img[idx+1] & 0b11111)

  r8 = (r5 * 255 + 15) // 31
  g8 = (g6 * 255 + 31) // 63
  b8 = (b5 * 255 + 15) // 31
  return RGB(r8, g8, b8)


def _arc_score(img, start_pixel):
  path_idx_to_img_idx = []
  path_idx_to_rgb = []
  for img_idx in bead_arc(start_pixel):
    path_idx_to_img_idx.append(img_idx)
    path_idx_to_rgb.append(_rgb_for_pixel(img, img_idx))
  path_idx_to_total_dist = [0] * BEAD_ARC_LEN

  for ((path_idx_a, rgb_a), (path_idx_b, rgb_b)) in itertools.combinations(enumerate(path_idx_to_rgb), 2):
    dist = rgb_dist(rgb_a, rgb_b)
    path_idx_to_total_dist[path_idx_a] += dist
    path_idx_to_total_dist[path_idx_b] += dist

  paths = sorted(enumerate(path_idx_to_total_dist), key=lambda pair: pair[1])[:12]

  total = sum((total_dist for (path_idx, total_dist) in paths))

  return ([path_idx_to_img_idx[path_idx] for (path_idx, _dist) in paths], total)

START_PIXELS = [y*IMG_WIDTH+x for x in range(15,21) for y in range(21,24)]

def bead_color_and_path(img):
  (pixels, score) = min((_arc_score(img, start_pixel) for start_pixel in START_PIXELS), key=lambda pair: pair[1])
  return (rgb_mean((_rgb_for_pixel(img, pixel) for pixel in pixels)), pixels)

def bead_color(img):
  return bead_color_and_path(img)[0]
