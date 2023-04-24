import itertools
import math
from collections import namedtuple

IMG_WIDTH = 40
IMG_HEIGHT = 30
IMG_SIZE = IMG_WIDTH * IMG_HEIGHT

RGB = namedtuple("RGB", "r g b")

def rgb_dist(a, b):
  rmean = (a.r + b.r) // 2
  r = a.r - b.r
  g = a.g - b.g
  b = a.b - b.b
  return math.isqrt(
      ((512*rmean)*r*r)>>8
      +
      4*g*g
      +
      ((767-rmean)*b*b)>>8
  )

def rgb_mean(rgb_iterable):
  count = 0
  sum_rgb = RGB(0, 0, 0)
  for rgb in rgb_iterable:
    count += 1
    sum_rgb.r += rgb.r * rgb.r
    sum_rgb.g += rgb.g * rgb.g
    sum_rgb.b += rgb.b * rgb.b

  if count == 0:
    return sum_rgb

  return RGB(
    math.isqrt(sum_rgb.r / count),
    math.isqrt(sum_rgb.g / count),
    math.isqrt(sum_rgb.b / count),
  )

def bead_arc(start_pixel):
  start_x = start_pixel % IMG_WIDTH
  start_y = start_pixel / IMG_WIDTH
  assert start_x < IMG_WIDTH-7
  assert start_y > 7

  idx = start_pixel
  for _ in range(6):
    idx -= IMG_WIDTH
    yield idx

  idx -= IMG_WIDTH - 1
  yield idx

  for _ in range(6):
    idx += 1
    yield idx

  idx += IMG_WIDTH + 1
  yield idx

  for _ in range(6):
    idx += IMG_WIDTH
    yield idx

def _rgb_for_pixel(img, pixel_idx):
  assert pixel_idx < IMG_SIZE
  idx = pixel_idx * 2
  red = img[idx] >> 3
  green = (img[idx] << 5) | (img[idx+1] >> 5)
  blue = img[idx+1] & 0b11111
  return RGB(red, green, blue)


def _arc_score(img, start_pixel):
  distances = {}

  for (a, b) in itertools.combinations(bead_arc(start_pixel), 2):
    dist = rgb_dist(_rgb_for_pixel(img, a), _rgb_for_pixel(img, b))
    distances.get(a, {})[b] = dist
    distances.get(b, {})[a] = dist

  while len(distances) > 10:
    (max_pixel, _max_dist) = max(((pixel, sum(dists)) for (pixel, dists) in distances), key=lambda pair: pair[1])
    del distances[max_pixel]
    for dists in distances.values():
      del dists[max_pixel]

  total = sum(sum(d.values()) for d in distances.values()) // 2

  return (distances.keys(), total)

START_PIXELS = [y*IMG_WIDTH+x for x in range(15,20) for y in range(15,20)]

def bead_color(img):
  (pixels, score) = min((_arc_score(img, start_pixel) for start_pixel in START_PIXELS), key=lambda pair: pair[1])
  return (rgb_mean((_rgb_for_pixel(img, pixel) for pixel in pixels)), pixels)

