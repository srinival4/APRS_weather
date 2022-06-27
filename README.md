A project for Raspberry Pi and Amateur Radio enthusiasts!
---------------------------------------------------------

APRS (Automatic Packet Reporting System) is an amateur radio-based system for real time digital communication of information of immediate value in a local area. It is used for communicating GPS coordinates, weather station telemetry, text messages, announcements, queries and other telemetry.

Data is ingested into an APRS -IS (APRS - Internet System), via an Internet connected receiver (IGate) and transmitted to all other stations using packet repeaters or digipeaters, using store and forward technology to retransmit packets.

With a Raspberry Pi Zero connected to a BME280 sensor (see my weather station GitHub repository to learn about setup), you can generate local weather readings (temperature, pressure, humidity) and transmit local weather readings via APRS from your backyard!

Steps

1.  pip install aprslib (install the aprs python library) onto your Raspberry Pi Zero.

2.  Find the passcode associated with your Amateur Radio callsign using the below link

<https://apps.magicbug.co.uk/passcode/index.php/passcode>

1.  Find your latitude, longitude using Google Maps.

2.  Download and Edit the APRS config file (aprs_wx.conf) with callsign (use <callsign>-13 for weather station)  latitude, longitude and passcode. If you want to send your latitude, longitude along with the weather packet (good idea to do so), then set position as True.

3.  Download the python program to collect weather data from BME280, form the ARPS packet and transmit it. (backyard_weather_station.py).

4.  Connect the BME280 sensor to the Raspberry Pi zero (refer to README in my weather_station repo for details).

5.  Run i2cdetect -1 y, note the address of your BME280 sensor.

6.  Edit the address of the chip in the backyard_weather_station.py file. Specifically, find the program line,  self.address= and put in the address from step 6. Save the file. 

7.  Run backyard_weather_station.py

8.  Log into aprs.fi. Click on Weather data. Search with your "callsign-13" to confirm that weather packet has been transmitted.
