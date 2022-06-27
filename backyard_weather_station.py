# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import configparser
import logging
import os
import sys
import time
from datetime import datetime

import bme280
import smbus2

import aprslib
from aprslib.util import latitude_to_ddm, longitude_to_ddm


class Chip:
    # function to intialize chip
    def __init__(self):
        self._port = 1
        self.bus = smbus2.SMBus(self._port)
        self.address = 0x76  # Adafruit BME280 address

    # function to take a reading
    def read_chip(self, bme280_data):
        self.humidity = round(bme280_data.humidity, 2)
        self.pressure = round(bme280_data.pressure, 2)
        self.ambient_temperature = round((bme280_data.temperature*9/5) +32, 2)
      


CONFIG_FILE = '/home/pi/weather/aprs_wx.conf'

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

def make_aprs_wx(wind_dir=None, wind_speed=None, wind_gust=None, temperature=None,
                 rain_last_hr=None, rain_last_24_hrs=None, rain_since_midnight=None,
                 humidity=None, pressure=None, position=False):
    wx_fmt = lambda n, l=3: '.' * l if n is None else "{:0{l}d}".format(int(n), l=l)
    if position == True:
        template = '{}/{}g{}t{}r{}p{}P{}h{}b{}'.format
    else:
        template = 'c{}s{}g{}t{}r{}p{}P{}h{}b{}'.format

    return template(wx_fmt(wind_dir),
                    wx_fmt(wind_speed),
                    wx_fmt(wind_gust),
                    wx_fmt(temperature),
                    wx_fmt(rain_last_hr),
                    wx_fmt(rain_last_24_hrs),
                    wx_fmt(rain_since_midnight),
                    wx_fmt(humidity, 2),
                    wx_fmt(pressure, 5))


def connect(call, password):
    ais = aprslib.IS(call, passwd=password, port=14580)
    for retry in range(5):
        try:
            ais.connect()
        except ConnectionError as err:
            logging.warning(err)
            time.sleep(5 * retry)
        else:
            return ais
        raise IOError('Connection Failed')

def main():
    logging.info('Read config file %s', CONFIG_FILE)
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    try:
        call = config.get('APRS', 'call')
        passcode = config.get('APRS', 'passcode')
        lat = config.getfloat('APRS', 'latitude', fallback=0.0)
        lon = config.getfloat('APRS', 'longitude', fallback=0.0)
        sleep_time = config.getint('APRS', 'sleep', fallback=900)
        position = config.getboolean('APRS', 'position', fallback=False)
    except configparser.Error as err:
        logging.error(err)
        sys.exit(os.EX_CONFIG)

    logging.info('Send weather data %s position', 'with' if position else 'without')
    BME280 = Chip()
    
    while True:
        try:
            bme280_data = bme280.sample(BME280.bus, BME280.address)
            logging.info('After bme280 call %s', bme280_data)
            if (bme280_data) is None:
                logging.debug("No reading from sensor")
                break;
            BME280.read_chip(bme280_data)
            logging.info('Ambient temperature %f',BME280.ambient_temperature)
            logging.info('Pressure %s', BME280.pressure)
            logging.info('Humidity %s', BME280.humidity)
            ais = connect(call, passcode)
            weather = make_aprs_wx(temperature=BME280.ambient_temperature, humidity=BME280.humidity, pressure=BME280.pressure, position=position)
            if position:
                ais.sendall("{}>APRS,TCPIP*:={}/{}_{}X".format(call, latitude_to_ddm(lat), longitude_to_ddm(lon),weather))
            else:
                _date = datetime.utcnow().strftime('%m%d%H%M')
                ais.sendall("{}>APRS,TCPIP*:_{}{}".format(call, _date, weather))
            ais.close()
        except IOError as err:
            logging.error(err)
            sys.exit(os.EX_IOERR)
        except Exception as err:
            logging.error(err)

        time.sleep(sleep_time)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


