from _http import start_http
from _scheduler import start_timer, load_scheduler
from _utils import flags, start_temp_updater
from _hap import start_hap
from config import ENABLE_SCHEDULER, ENABLE_HAP, ENABLE_TEMPERATURE_SENSOR, ENABLE_HTTP
import logging
from logging.handlers import TimedRotatingFileHandler

logging.basicConfig(level=logging.INFO, format='[%(levelname)7s][%(asctime)s] %(message)s')

threads = {}

if __name__ == "__main__":
	try:
		load_scheduler()

		if ENABLE_HTTP:
			threads['HTTP'] = start_http()
		if ENABLE_TEMPERATURE_SENSOR:
			threads['TEMP'] = start_temp_updater()
		if ENABLE_HAP:
			threads['HAP'] = start_hap()
		if ENABLE_SCHEDULER:
			threads['SCHED'] = start_timer()

		for t in threads:
			threads[t].start()
		for t in threads:
			threads[t].join()

	except:
		for t in threads:
			logging.info("Shutting down {}...".format(t))
			threads[t].stop_main()
