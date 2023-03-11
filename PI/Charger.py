import busio
import smbus
import board
import atexit
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep
import RPi.GPIO as GPIO
from enum import IntEnum
import struct

#pin defines
PILOT_PIN = 13
ENABLE_CAR_PIN = 27
ENABLE_DRYER_PIN = 22
RELAY1_TEST = 5
RELAY2_TEST = 6

#ADS init
i2c = busio.I2C(board.SCL, board.SDA, frequency = 3400000)
ads_read = ADS.ADS1015(i2c, address = 0x48, data_rate = 3300, mode = ADS.Mode.CONTINUOUS)
#ads_read = ADS.ADS1115(i2c, address = 0x49, data_rate = 860, mode = ADS.Mode.CONTINUOUS)
ads_read.gain = 1
PILOT_READ = AnalogIn(ads_read, ADS.P0)
#i2c = smbus.SMBus(1)

GPIO.setmode(GPIO.BCM)

#GPIO init
GPIO.setup(ENABLE_CAR_PIN, GPIO.OUT)
GPIO.setup(ENABLE_DRYER_PIN, GPIO.OUT)
GPIO.setup(PILOT_PIN, GPIO.OUT)
GPIO.setup(RELAY1_TEST, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RELAY2_TEST, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#GPIO pwm init
PILOT = GPIO.PWM(PILOT_PIN, 1000)

#enum define
class Charge_Side(IntEnum):
    DRYER_SIDE = 1
    CAR_SIDE = 2
    NEITHER = 3

class EV_State(IntEnum):
    _order_ = 'ERROR VENT EV_CHARGE CONNECTED NOT_CONNECTED UNKNOWN'
    ERROR = 0
    VENT = 3
    EV_CHARGE = 6
    CONNECTED = 9
    NOT_CONNECTED = 12
    UNKNOWN = -1

SIDE = Charge_Side.CAR_SIDE
STATE = EV_State.UNKNOWN



def init_charger():
    if(SIDE is Charge_Side.CAR_SIDE):
        print("Initializing car chargin peripherals...")
        GPIO.output(PILOT_PIN, True)
    elif(SIDE is Charge_Side.DRYER_SIDE):
        print("Initializing dryer side peripherals...")

def enable_relay(side):
    GPIO.output(ENABLE_CAR_PIN, False)
    GPIO.output(ENABLE_DRYER_PIN, False)
    sleep(1)
    if(side is Charge_Side.CAR_SIDE):
        print("Car side relay enabled.")
        GPIO.output(ENABLE_CAR_PIN, True)
        GPIO.output(ENABLE_DRYER_PIN, False)
    elif(side is Charge_Side.DRYER_SIDE):
        print("Dryer side relay enabled.")
        GPIO.output(ENABLE_CAR_PIN, False)
        GPIO.output(ENABLE_DRYER_PIN, True)
    elif(side is Charge_Side.NEITHER):
        print("Both sides disabled.")
        GPIO.output(ENABLE_CAR_PIN, False)
        GPIO.output(ENABLE_DRYER_PIN, False)

def read_pilot_state():
    readings = []
    for i in range(100):
        readings.append(PILOT_READ.voltage)
        sleep(0.0001)
    
    readings_max = max(readings)
    readings_min = min(readings)
    Vpwm = (readings_max*6.57)-11.87

    diff = []
    states = [state for state in EV_State]
    for state in EV_State:
        diff.append(abs(Vpwm - int(state)))

    curr_state = states[diff.index(min(diff))]

    return curr_state

def test_side_enabled():
    return Charge_Side.CAR_SIDE if GPIO.input(RELAY1_TEST) else Charge_Side.DRYER_SIDE if GPIO.input(RELAY2_TEST) else Charge_Side.NEITHER

def exit():
    print("EXITED")
    enable_relay(Charge_Side.NEITHER)
    GPIO.cleanup()
atexit.register(exit)

PILOT.start(50)
enable_relay(Charge_Side.CAR_SIDE)
sleep(1)
while(1):
    print(read_pilot_state())
    sleep(1)
    print(test_side_enabled())
