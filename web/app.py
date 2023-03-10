from flask import Flask, request, render_template
# import RPi.GPIO as gpio
# import time
# import math
# import sys
# import os

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


# @app.before_request
# def before_request():
#     if not request.is_secure:
#         url = request.url.replace('http://', 'https://', 1)
#         code = 301
#         return redirect(url, code=code)


@app.route('/', methods=['GET', 'POST'])
def index():
    currOut = 1
    if request.method == 'POST':
        form = request.form
        currOut = currentOutput(form)
        # lightOn()

    return render_template('index.html', currOut=currOut)


def currentOutput(form):
    out = request.form['currentRange']
    # ads1115.set_addr_ADS1115(0x48)
    # ads1115.set_gain(ADS1115_REG_CONFIG_PGA_6_144V)
    # adc0 = ads1115.read_voltage(0)

    # return (adc0['r'])
    return out


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
