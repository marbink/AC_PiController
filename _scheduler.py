import logging, json
from threading import Thread
from datetime import datetime
from time import sleep, time
from _ir_tx import transmit, convert_to_pulses
from _utils import flags
from config import IR_COMMANDS

def _udp_loop_exit():
	flags.timerKill = True

def start_timer():
	logging.info("Starting scheduler loop...")
	t = Thread(target=_timer_loop)
	t.stop_main = _udp_loop_exit
	return t
	
def _timer_loop():
	scheduler = flags.status["scheduler"]["tasks"]
	last_executed_second = -1
	flags.status['scheduler']['enabled'] = True
	flags.status['scheduler']['enabled_since'] = int(time())
	while(not flags.timerKill):
		now_dt = datetime.now()
		seconds_since_midnight = int((now_dt - now_dt.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
		#logging.info(seconds_since_midnight)
		if not seconds_since_midnight == last_executed_second:
			last_executed_second = int(seconds_since_midnight)
			task = scheduler.get(str(seconds_since_midnight), None)
			if task is not None:
				logging.info("Executing scheduled command...")
				Thread(target=_execute_task, args=(task,)).start()
		sleep(0.5)
	flags.timerKill = False
	flags.status['scheduler']['enabled'] = False
	flags.status['scheduler']['enabled_since'] = None

def _execute_task(task):
	if task in IR_COMMANDS:
		logging.info("Executing task {}".format(task))
		flags.status["last_command"]["executed_by"] = "SCHEDULER"
		flags.status["last_command"]["command"] = task
		transmit(convert_to_pulses(IR_COMMANDS.get(task)))
	else:
		logging.info("Task {} not found. Skipping.".format(task))

def load_scheduler():
	tasks = {}
	try:
		with open('scheduler.json') as json_data:
			d = json.load(json_data)
			tasks = d
	except:
		logging.warning("scheduler.json file not found or not parsed correctly. Check if file exists and if syntax is correct.")
		pass
	logging.debug(tasks)
	flags.status["scheduler"]["tasks"] = tasks