import logging
import signal
from threading import Thread
from pyhap.accessory_driver import AccessoryDriver
import pyhap.loader as loader
from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_THERMOSTAT
from _utils import flags, get_temperature
from _ir_tx import transmit, convert_to_pulses

class Thermostat(Accessory):

    category = CATEGORY_THERMOSTAT

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        serv_Thermostat = self.add_preload_service('Thermostat')
        self.char_CurrentHeatingCoolingState = serv_Thermostat.configure_char(
        	'CurrentHeatingCoolingState', getter_callback=self.get_current_heatingcoolingstate) 
            #[0, 1, 2, 3] ([off, heat, cool, auto])

        self.char_TargetTemperature = serv_Thermostat.configure_char(
        	'TargetTemperature', getter_callback=self.get_target_temperature, setter_callback=self.set_target_temperature)
        new_properties = {	'minValue': flags.status.get("min_temperature", 15),
        					'maxValue': flags.status.get("max_temperature", 35),
        					'step': 1
        				}
        self.char_TargetTemperature.override_properties(properties=new_properties)

        self.char_TemperatureDisplayUnits = serv_Thermostat.configure_char(
        	'TemperatureDisplayUnits')

        self.char_CurrentTemperature = serv_Thermostat.configure_char(
        	'CurrentTemperature')

        self.char_TargetHeatingCoolingState = serv_Thermostat.configure_char(
        	'TargetHeatingCoolingState', getter_callback=self.get_target_heatingcoolingstate, setter_callback=self.set_target_heatingcoolingstate)
            #[0, 1, 2, 3] ([off, heat, cool, auto])

    @Accessory.run_at_interval(3)
    def run(self):
        self.char_CurrentTemperature.set_value(get_temperature())

    def set_target_temperature(self, value):
        flags.status['target_temperature'] = value
        if flags.status['target_heatingcoolingstate'] != 0: # Not OFF
            transmit(convert_to_pulses(create_command()))

    def get_target_temperature(self):
        return flags.status['target_temperature']
        
    def set_target_heatingcoolingstate(self, value):
        flags.status['target_heatingcoolingstate'] = value
        transmit(convert_to_pulses(create_command()))

    def get_target_heatingcoolingstate(self):
        return flags.status['target_heatingcoolingstate']

    def get_current_heatingcoolingstate(self):
        return flags.status['current_heatingcoolingstate']

def start_hap():
	driver = AccessoryDriver(port=51826)
	driver.add_accessory(accessory=Thermostat(driver, flags.status.get("device_name", "HAP_NAME")))
	signal.signal(signal.SIGTERM, driver.signal_handler)
	t = Thread(target=driver.start)
	t.stop_main = driver.stop
	return t

def create_command():
    temp = flags.status['target_temperature']
    hc_state = flags.status['target_heatingcoolingstate']

    states = {
        "0": "OFF",
        "1": "HEAT",
        "2": "COOL",
        "3": "AUTO"
    }

    state = states.get(hc_state, "OFF")
    if state == "OFF":
        return "AC_OFF"

    state = "AUTO" # hardcoded as I won't use HEAT or COOL mode.
    return "AC_ON_{}DEG_{}".format(temp, state)
