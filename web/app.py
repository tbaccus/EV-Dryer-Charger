from flask import Flask, jsonify, request, render_template
import RPi.GPIO as gpio
import time
import math
import sys
import os

sys.path.append('../')
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from DFRobot_ADS1115 import ADS1115
ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16
ads1115 = ADS1115()

app = Flask(__name__)
# gpio.setmode(gpio.BCM)
# gpio.setup(4, gpio.OUT)
# gpio.setup(27, gpio.OUT)
  
@app.route('/', methods=['GET', 'POST'])
def index():
  QTc_result = False
  if request.method == 'POST':
    form = request.form
    QTc_result = calculate_qtc(form)
    # lightOn()

  return render_template('index.html', QTc_result=QTc_result)

@app.route('/g')
def g():
  # gpio.output(4, gpio.HIGH)
  # gpio.output(27, gpio.LOW)

  return render_template('main.html')

@app.route('/r')
def r():
  # gpio.output(4, gpio.LOW)
  # gpio.output(27, gpio.HIGH)

  return render_template('main.html')

def calculate_qtc(form):
  ads1115.set_addr_ADS1115(0x48)
  ads1115.set_gain(ADS1115_REG_CONFIG_PGA_6_144V)
  adc0 = ads1115.read_voltage(0)

  # sex = request.form['sex']
  # heart_rate = int(request.form['hr'])
  # qt_int = int(request.form['qt'])
 
  # qt_seconds = qt_int / 1000 
  # rr_interval = (6000 / heart_rate) 
  # QTc = qt_seconds / math.sqrt(rr_interval) 
  # formated_QTc = round((QTc * 1000) * 10, 0)
  
  # if (formated_QTc > 440 and sex == 'm') or (formated_QTc > 460 and sex == 'f'):
  #   prolonged = True
  # else:
  #   prolonged = False
  
  return (adc0['r'])

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80, debug=True)