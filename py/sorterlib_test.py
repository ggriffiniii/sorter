import unittest
import itertools
from sorterlib import RGB, bead_color, bead_arc, rgb_dist, IMG_WIDTH, IMG_HEIGHT

class SorterLibTest(unittest.TestCase):
  def test_rgb_dist(self):
    a = RGB(255,255,255)
    b = RGB(255,255,255)
    self.assertEqual(
        rgb_dist(RGB(255,255,255), RGB(255,255,255)),
        0
    )
    self.assertTrue(
        rgb_dist(RGB(255,0,0), RGB(127,0,0))
        <
        rgb_dist(RGB(255,0,0), RGB(0,0,0))
    )

  def test_bead_arc(self):
    #self.assertEqual(list(bead_arc(1160)), [1,2,3])
    self.assertEqual(len(list(itertools.combinations(bead_arc(1160), 2))), 10)

  def test_bead_color(self):
    img = bytearray(2 * IMG_WIDTH * IMG_HEIGHT)
    self.assertEqual(None, bead_color(img))
