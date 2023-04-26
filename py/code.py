import board
import digitalio
import pwmio
import time
import usb_cdc
from adafruit_motor import servo
from adafruit_ov7670 import (OV7670, OV7670_SIZE_DIV16, OV7670_COLOR_RGB)

SERVO_MAX_RANGE=300
SERVO_MIN_PULSE=500
SERVO_MAX_PULSE=2500

hopper_servo = servo.Servo(
        pwmio.PWMOut(board.A0, frequency=50),
        actuation_range=SERVO_MAX_RANGE,
        min_pulse=SERVO_MIN_PULSE,
        max_pulse=SERVO_MAX_PULSE)

CHUTE_SERVO_RANGE=100
chute_servo = servo.Servo(
        pwmio.PWMOut(board.A1, frequency=50),
        actuation_range=CHUTE_SERVO_RANGE,
        min_pulse=500,
        max_pulse=SERVO_MAX_PULSE // (SERVO_MAX_RANGE // CHUTE_SERVO_RANGE))

cam_led = pwmio.PWMOut(board.D25, frequency=1000)
cam = OV7670(
  board.I2C(),
  data_pins=[board.D4, board.D5, board.D6, board.D9, board.D10, board.D11, board.D12, board.D13],
  clock=board.MOSI,
  vsync=board.MISO,
  href=board.RX,
  mclk=board.TX,
)
cam.size = OV7670_SIZE_DIV16
cam.colorspace = OV7670_COLOR_RGB

def capture(buffer):
  time.sleep(0.2)
  cam.capture(buffer)

class ServoTracker(object):
    DEGREES_PER_SEC = 240
    def __init__(self, degrees_to_travel):
        self.arrival_time = time.monotonic() + (degrees_to_travel / ServoTracker.DEGREES_PER_SEC)
    
    def wait(self, pause=0.0):
        time.sleep(self.arrival_time + pause - time.monotonic())
    
def move_servo(s, angle):
    degrees_to_travel = abs(s.angle - angle)
    s.angle = angle
    return ServoTracker(degrees_to_travel)

img_size = int(cam.width * cam.height)
img = bytearray(2 * img_size)

SIX_O_CLOCK_ANGLE=48
CAM_ANGLE=150
ROW_ANGLES = [
    200,
    215,
    233,
    255,
]

DROP_ANGLE=175
SLICE_0_ANGLE=6
SLICE_MULTIPLE=6.7

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
  cam_led.duty_cycle = 65535*75//100
  hopper_servo.angle=DROP_ANGLE
  chute_servo.angle=0
  while True:
    run()

def run():
  move_servo(hopper_servo, SIX_O_CLOCK_ANGLE-15).wait(0.1)
  move_servo(hopper_servo, SIX_O_CLOCK_ANGLE+15).wait(0.1)
  move_servo(hopper_servo, SIX_O_CLOCK_ANGLE).wait(0.25)
  move_servo(hopper_servo, CAM_ANGLE).wait(0.2)
  capture(img)
  bead_color = sorterlib.bead_color(img)
  (best_tube, color_dist) = best_tube_for_color(bead_color)
  if color_dist < COLOR_DIST_THRESHOLD or len(tubes) == MAX_TUBES:
    best_tube.count += 1
  else:
    best_tube = Tube(len(tubes), bead_color)
    tubes.append(tube)

  move_servo(chute_servo, SLICE_0_ANGLE+(best_tube.slice_idx()*SLICE_MULTIPLE))
  move_servo(hopper_servo, ROW_ANGLES[best_tube.row_idx()]).wait(0.2)
  move_servo(hopper_servo, DROP_ANGLE).wait(0.2)

if __name__ == "__main__":
  loop()

