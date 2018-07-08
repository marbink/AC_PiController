# Don't modify!

import logging
from threading import Thread
from config import IR_COMMANDS, MIN_TEMPERATURE, MAX_TEMPERATURE, DEVICE_NAME, DEFAULT_TARGET_TEMPERATURE, DEFAULT_TARGET_HEATINGCOOLINGSTATE, DEFAULT_CURRENT_HEATINGCOOLINGSTATE
from time import sleep, time

class flags:
	tempKill = False # Used to stop thread
	timerKill = False # Used to stop thread
	pulses = None # array containing pluses still waiting to be transmitted
	pusles_transmit_time = None
	transmit_thread = None
	status = {
		"version": 0.10,
		"temperature_sensor": {
			"value": None,
			"last_update": None
		},
		"last_command": {
			"command": None,
			"executed_by": None,
		},
		"scheduler": {
			"enabled": None,
			"enabled_since": None,
			"tasks": None,
		},
		"swinging": False,
		"available_commands": list(IR_COMMANDS.keys()),
		"device_name": DEVICE_NAME,
		"min_temperature": MIN_TEMPERATURE,
		"max_temperature": MAX_TEMPERATURE,
		"target_temperature": DEFAULT_TARGET_TEMPERATURE,
		"target_heatingcoolingstate": DEFAULT_TARGET_HEATINGCOOLINGSTATE,
		"current_heatingcoolingstate": DEFAULT_CURRENT_HEATINGCOOLINGSTATE
	}

def get_temperature(): # I use a DS18B20
	temp = flags.status.get("temperature_sensor", 0).get("value", 0)
	return 0 if temp is None else temp

def _temp_reading_loop_exit():
	flags.tempKill = True

def start_temp_updater():
	logging.info("Starting temperature sensor reading loop...")
	t = Thread(target=_temp_reading_loop)
	t.stop_main = _temp_reading_loop_exit
	return t

def _temp_reading_loop():
	try:
		from w1thermsensor import W1ThermSensor
		sensor = W1ThermSensor()
		while(not flags.tempKill):
			flags.status['temperature_sensor']['value'] = sensor.get_temperature()
			flags.status['temperature_sensor']['last_update'] = int(time())
			sleep(1)
	except:
		logging.error("Something wrong with w1 library (maybe it cannot load w1 therm kernel modules)")
	