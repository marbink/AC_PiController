# AC_PiController
My HomeKit implementation to remote control my A/C.

## What is this?
As my A/C has not a scheduler function, neither a network port to control it, I decided to create this little project to have a semi-automatic use of my A/C using an IR Led and a Raspberry Pi.

I decided to share it as this can be a good base to develop your own solution.

This project consists in different parts:
- HTTP Server (few ugly buttons are shown on port 80): it's just to test stuff as I currently use Home app and Siri on my iPhone (HomeKit).
- HAP Server: HomeKit support. You can use Siri or Home app on iPhone to control AC.
- Scheduler: I have a shitty low cost AC. It does not have anything special. No WiFi, No scheduled tasks.
- Temperature Sensor reading: I added a temperature sensor. Not many functions I coded for it, it is just a reading at the moment. Can be used for some useful things (See Ideas paragraph)
- IR transmitter (codes are hardcoded, more info are written in config.py and in docs folder.)


## Requirements
- I used a Raspberry Pi 1 Model B with Raspbian Stretch Lite. I will probably move it on a Raspberry Pi Zero W to reduce size and to use built-in WiFi instead of Ethernet.
- Working IR LED on GPIO port (there are a lot of projects on the web showing how to build one, it's really cheap.)
- Python 3 (Should be already preinstalled in Raspbian Stretch Lite)


## My Setup
- Raspberry Pi 1 Model B + Raspbian Stretch Lite
- DS18B20 with its data pin connected to GPIO.4 (There are a lot of tutorials on how to connect it, it needs a resistor and nothing more).
- IR Led on GPIO.25 (I used one I got from an old broken TV remote control. Lot of schemas are available for this too on the web).

## Installation
1. You require pigpiod, if it's not already installed use this command to install it:
`sudo apt install pigpiod`

2. Install some required python modules
`sudo pip3 install -r requirements.txt`

# How to launch
Pigpiod needs to be launched too.

`sudo systemctl start pigpiod`
- or -
`sudo pigpiod`

then

`sudo python3 start.py`


## Other

To set pigpiod to run whe Pi boots:
`sudo systemctl enable pigpiod`


## Ideas (Not sure i'll work on them, PRs are appreciated though)
- Use a thermal sensor (example: ds18b20) to avoid some tasks if AC does not need to work as the room temperature is not high.
- Implement ability to control relay on a GPIO port. (can be used to turn ON/OFF a light for example)
- Implement DB to store temperatures (maybe to show a graph on web side) and store all activities made by app. (sqlite3?)
- Use flask for http server. Maybe bootstrap for UI and implement some cute functions or statistics.
