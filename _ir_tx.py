#!/usr/bin/env python

import pigpio, logging
from threading import Thread
from time import time, sleep
from config import IR_TX_GPIO_PIN, IR_TX_FREQUENCY
from _utils import flags

class tx:

	"""
	Credits: joan - https://www.raspberrypi.org/forums/viewtopic.php?t=79978
	"""

	def __init__(self, pi, gpio, carrier_hz):

		"""
		Initialises an IR tx on a Pi's gpio with a carrier of
		carrier_hz.

		http://www.hifi-remote.com/infrared/IR-PWM.shtml
		"""

		self.pi = pi
		self.gpio = gpio
		self.carrier_hz = carrier_hz
		self.micros = int(1000000 / carrier_hz)
		self.on_mics = int(self.micros / 2)
		self.off_mics = int(self.micros - self.on_mics)
		self.offset = 0

		self.wf = []
		self.wid = -1

		pi.set_mode(gpio, pigpio.OUTPUT)

	def clear_code(self):
		self.wf = []
		if self.wid >= 0:
			self.pi.wave_delete(self.wid)
			self.wid = -1

	def construct_code(self):
		if len(self.wf) > 0:
			pulses = self.pi.wave_add_generic(self.wf)
			#print("waveform TOTAL {} pulses".format(pulses))
			self.wid = self.pi.wave_create()

	def send_code(self):
		if self.wid >= 0:
			self.pi.wave_send_once(self.wid)
			while self.pi.wave_tx_busy():
				pass

	def add_to_code(self, on_micros, off_micros):
		"""
		Add on micros of carrier followed by off micros of silence.
		"""
		# Calculate cycles of carrier.
		on = int((on_micros + self.on_mics) / self.micros)

		# Is there room for more pulses?

		if (on*2) + 1 + len(self.wf) > 680: # 682 is maximum
			
			pulses = self.pi.wave_add_generic(self.wf)
			#print("waveform partial {} pulses".format(pulses))
			self.offset = self.pi.wave_get_micros()

			# Continue pulses from offset.
			self.wf = [pigpio.pulse(0, 0, self.offset)]

		# Add on cycles of carrier.
		for x in range(int(on)):
			self.wf.append(pigpio.pulse(1<<self.gpio, 0, self.on_mics))
			self.wf.append(pigpio.pulse(0, 1<<self.gpio, self.off_mics))

		# Add off_micros of silence.
		self.wf.append(pigpio.pulse(0, 0, off_micros))

def transmit(p):
	flags.pulses = p
	flags.pusles_transmit_time = int(time()) + 2 # Adds 2 seconds to avoid too fast commands.
	if flags.transmit_thread is None or not flags.transmit_thread.isAlive():
		flags.transmit_thread = Thread(target=_transmit)
		flags.transmit_thread.start()

def _transmit():
	while(flags.pulses is not None):
		sleep(1)
		if flags.pusles_transmit_time < time():
			p = flags.pulses
			flags.pulses = None
			if True: #try:
				import pigpio
				import _ir_tx

				pulses = (len(p)/2) * 2
				pi = pigpio.pi() # Connect to local Pi.
				tx = _ir_tx.tx(pi, IR_TX_GPIO_PIN, IR_TX_FREQUENCY) # Pi, IR gpio, carrier frequency Hz.
				tx.clear_code()

				for x in range(0, int(pulses), 2):
					tx.add_to_code(int(p[x]), int(p[x+1]))

				tx.construct_code()
				tx.send_code()
				tx.clear_code()
				pi.stop()
			#except:
			#	pass
	
def convert_to_pulses(bin_string, pause=600, zero=500, one=1600, repeat=2, repeat_pause=5100, header=(4500, 4300)):
	pulses_array = []
	
	for r in range(0, repeat):
		for i in header:
			pulses_array.append(i)
		for i in bin_string:
			pulses_array.append(pause)
			pulses_array.append(one if i == "1" else zero)
		pulses_array.append(pause)
		pulses_array.append(repeat_pause)
		
	return pulses_array

#Example	
#transmit(convert_to_pulses("101100100100110101111011100001001110000000011111"))
