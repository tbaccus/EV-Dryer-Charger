import RPi.GPIO as g
import time

g.setmode(g.BCM)

g.setup(4, g.OUT)
g.setup(27, g.OUT)

for i in range(10):
  time.sleep(0.2)
  g.output(4, g.LOW)
  g.output(27, g.HIGH)
  time.sleep(0.2)
  g.output(4, g.HIGH)
  g.output(27, g.LOW)

g.cleanup()