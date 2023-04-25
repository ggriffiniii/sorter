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
      (((512+rmean)*r*r)>>8)
      +
      4*g*g
      +
      (((767-rmean)*b*b)>>8)
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
    math.isqrt(sum_rgb.r // count),
    math.isqrt(sum_rgb.g // count),
    math.isqrt(sum_rgb.b // count),
  )

def bead_arc(start_pixel):
  start_x = start_pixel % IMG_WIDTH
  start_y = start_pixel / IMG_WIDTH
  assert start_x < IMG_WIDTH-7
  assert start_y > 7

  idx = start_pixel
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
  distances = {}

  for (a, b) in itertools.combinations(bead_arc(start_pixel), 2):
    rgb_a = _rgb_for_pixel(img, a)
    rgb_b = _rgb_for_pixel(img, b)
    dist = rgb_dist(rgb_a, rgb_b)
    a_distances = distances.get(a, {})
    a_distances[b] = dist
    distances[a] = a_distances

    b_distances = distances.get(b, {})
    b_distances[a] = dist
    distances[b] = b_distances

  while len(distances) > 12:
    (max_pixel, _max_dist) = max(
        (
            (pixel, sum(dists.values()))
            for (pixel, dists)
            in distances.items()
        ),
        key=lambda pair: pair[1]
    )
    del distances[max_pixel]
    for dists in distances.values():
      del dists[max_pixel]

  total = sum(sum(d.values()) for d in distances.values()) // 2

  return (distances.keys(), total)

START_PIXELS = [y*IMG_WIDTH+x for x in range(15,21) for y in range(18,22)]

def bead_color(img):
  (pixels, score) = min((_arc_score(img, start_pixel) for start_pixel in START_PIXELS), key=lambda pair: pair[1])
  return (rgb_mean((_rgb_for_pixel(img, pixel) for pixel in pixels)), pixels)

