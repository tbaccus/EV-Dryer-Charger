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
import threading
from threading import Thread
from threading import Lock

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
CURRENT_READ = AnalogIn(ads_read, ADS.P1)
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
    _order_ = 'SHUTOFF VENT EV_CHARGE CONNECTED NOT_CONNECTED ERROR'
    SHUTOFF = 0
    VENT = 3
    EV_CHARGE = 6
    CONNECTED = 9
    NOT_CONNECTED = 12
    ERROR = -1

class Charging_State(IntEnum):
    CHARGING, OVER_CURRENT, RELAY_FAULT, SHUTOFF_CAR_STATE, ERROR_CAR_STATE, VENT_CAR_STATE = range(1, 7)

CHARGING_STATE = Charging_State.CHARGING
SIDE = Charge_Side.CAR_SIDE
STATE = EV_State.UNKNOWN
THREAD_LOCK = threading.lock()

# def init_charger():
#     if(SIDE is Charge_Side.CAR_SIDE):
#         print("Initializing car charging peripherals...")
#         GPIO.output(PILOT_PIN, True)
#     elif(SIDE is Charge_Side.DRYER_SIDE):
#         print("Initializing dryer side peripherals...")

def read_current():
    return (CURRENT_READ.voltage/5)*20

def enable_relay(side):
    global SIDE
    SIDE = side
    GPIO.output(ENABLE_CAR_PIN, False)
    GPIO.output(ENABLE_DRYER_PIN, False)
    sleep(0.5)
    if(SIDE is Charge_Side.CAR_SIDE):
        print("Car side relay enabled.")
        GPIO.output(ENABLE_CAR_PIN, True)
        GPIO.output(ENABLE_DRYER_PIN, False)
    elif(SIDE is Charge_Side.DRYER_SIDE):
        print("Dryer side relay enabled.")
        GPIO.output(ENABLE_CAR_PIN, False)
        GPIO.output(ENABLE_DRYER_PIN, True)
    elif(SIDE is Charge_Side.NEITHER):
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
    haultCharge()
    enable_relay(Charge_Side.NEITHER)
    GPIO.cleanup()
atexit.register(exit)

# PILOT.start(50)
# enable_relay(Charge_Side.CAR_SIDE)
# sleep(1)
# while(1):
#     print(read_pilot_state())
#     sleep(1)
#     print(test_side_enabled())
#     print("CURRENT: ", read_current(), " A")

def enableCharging():
    stuckRelayCheck()
    while(True):
        if(SIDE is Charge_Side.DRYER_SIDE): 
            enableDryerSide()
        elif(SIDE is Charge_Side.CAR_SIDE):
            enableCarSide()

def haultCharge():
    PILOT.stop()
    GPIO.output(PILOT_PIN, False)
    sleep(1)


def stuckRelayCheck():
    enable_relay(Charge_Side.NEITHER)
    print("Stuck relay test...")
    while(test_side_enabled() is not Charge_Side.NEITHER): 
        print("Relay is stuck or ground fault has occured.")
        sleep(0.5) 

def enableDryerSide():
    #switch to dryer side
    haultCharge()
    enable_relay(Charge_Side.DRYER_SIDE)

def enableCarSide():
    global CHARGING_STATE
    initiatePilotReadyWait()
    initiateCharging() #<-switch to car side
    callChargingSafetyCheckThreads()
    while(SIDE is Charge_Side.CAR_SIDE):
        if(CHARGING_STATE is Charging_State.OVER_CURRENT and SIDE is Charge_Side.CAR_SIDE):
            haultCharge()
            enable_relay(Charge_Side.NEITHER)
            sleep(300)
            initiatePilotReadyWait()
            initiateCharging()
        if(CHARGING_STATE is not Charging_State.CHARGING and SIDE is Charge_Side.CAR_SIDE):
            print("Charging state haulted due to fault: ", CHARGING_STATE)
            enableDryerSide()
            break

def callChargingSafetyCheckThreads():
    current_thread = Thread(target = overCurrentTest)
    car_state_thread = Thread(target = carStateTest)
    relay_state_thread = Thread(target = relayStateBadGroundTest)
    current_thread.run()
    car_state_thread.run()
    relay_state_thread.run()


def setChargingState(state):
    global CHARGING_STATE, THREAD_LOCK
    THREAD_LOCK.acquire()
    CHARGING_STATE = state
    THREAD_LOCK.release()

# This function initiates the pilot signal 
# and waits for a ready signal from the car.
def initiatePilotReadyWait():
    GPIO.output(PILOT_PIN, True)
    while(STATE is not EV_State.CONNECTED):
        print("Waiting for EV to be connected...")
        sleep(0.5)
    PILOT.start(20)

def initiateCharging():
    enable_relay(Charge_Side.CAR_SIDE)

def overCurrentTest():
    global SIDE
    sleep(0.5)
    while(SIDE = Charge_Side.CAR_SIDE):
        if(read_current() >= 12):
            setChargingState(Charging_State.OVER_CURRENT)
            

def relayStateBadGroundTest():
    global SIDE
    while(SIDE = Charge_Side.CAR_SIDE):
        if(test_side_enabled() is not Charge_Side.CAR_SIDE): #relay state error or badground
            setChargingState(Charging_State.RELAY_FAULT)

def carStateTest():
    global SIDE
    while(SIDE = Charge_Side.CAR_SIDE):
        car_state = read_pilot_state()
        if(car_state is EV_State.ERROR):
            setChargingState(Charging_State.ERROR_CAR_STATE)
        if(car_state is EV_State.SHUTOFF):
            setChargingState(Charging_State.SHUTOFF_CAR_STATE)
        if(car_state is EV_State.VENT):
            setChargingState(Charging_State.VENT_CAR_STATE)