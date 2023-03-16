from flask import Flask, request, render_template
from apscheduler.schedulers.sync import Scheduler
from apscheduler.triggers.interval import IntervalTrigger
import RPi.GPIO as GPIO
import time
# import math
import sys
import os
import threading

sys.path.insert(1, "../PI")
import Charger

# sys.path.append('../')
# sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# from DFRobot_ADS1115 import ADS1115
# ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
# ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
# ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
# ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
# ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
# ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16
# ads1115 = ADS1115()

app = Flask(__name__)
# gpio.setmode(gpio.BCM)
# gpio.setup(4, gpio.OUT)
# gpio.setup(27, gpio.OUT)


@app.route('/', methods=['GET', 'POST'])
def index():
    currOut = 1
    if request.method == 'POST':
        form = request.form
        currOut = currentOutput(form)

    return render_template('index.html', currOut=currOut)


def currentOutput(form):
    out = request.form['currentRange']
    print(request.form)
    #GPIO.output(Charger.PILOT_PIN, True)
    #Charger.PILOT.start(50)
    if (request.form['dryerSwitch'] == 'true'):
        Charger.SIDE = Charger.Charge_Side.CAR_SIDE
    else:
        Charger.SIDE = Charger.Charge_Side.DRYER_SIDE

    # scheduler = Scheduler()
    # scheduler.add_schedule(index, IntervalTrigger(seconds=1), id="test")
    # scheduler.start_in_background()
    # ads1115.set_addr_ADS1115(0x48)
    # ads1115.set_gain(ADS1115_REG_CONFIG_PGA_6_144V)
    # adc0 = ads1115.read_voltage(0)

    # return (adc0['r'])
    return out

def test():
    print("hi")

if __name__ == "__main__":
    Charger.SIDE = Charger.Charge_Side.CAR_SIDE
    t1 = threading.Thread(target=Charger.enableCharging)
    t1.start()
    app.run(host='0.0.0.0', port=80, debug=True)
    # t1 = threading.Thread(target=test2)
    # t2 = threading.Thread(target=test)

    # t1.start()
    # t2.start()

    # t1.join()
    # t2.join()
