from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from _utils import flags
from config import IR_COMMANDS, HTTP_LOG_EVERY_REQUEST
from _ir_tx import transmit, convert_to_pulses
import json
import logging

def _GET_response_status(args):
	return '{{"status":"OK","data":{0}}}'.format(json.dumps(flags.status))

def _GET_response_commands(args):
	if args is not None:
		cmd = IR_COMMANDS.get(args['CMD'], None)
		if cmd is not None:
			logging.info("Executing command {}".format(args['CMD']))
			flags.status["last_command"]["executed_by"] = "MANUAL"
			flags.status["last_command"]["command"] = args['CMD']
			transmit(convert_to_pulses(cmd))
			return '{"status":"OK"}';
		else:
			return '{"status":"ERROR", "data":"COMMAND_NOT_FOUND"}';
	else:
		# I don't care about ugly GUI as I won't use it.
		return """
		<div id="container"></div>
		<script>
			function callCommand(item)
			{{	
				var xhttp = new XMLHttpRequest();
				xhttp.open("GET", "/commands?cmd="+item, true);
				xhttp.send();
			}}
			var commands = '{}'.split(',').sort();
			commands.forEach(function(entry) {{
				var button_html = `<button type="button" onclick="callCommand('`+entry+`')" href="#">`+entry+`</button>`;
				document.getElementById('container').innerHTML += button_html;
			}});
		</script>
		""".format(
			",".join(str(x) for x in IR_COMMANDS) 
	)

GET_paths = {
	'/': ('html', _GET_response_commands),
	'/status': ('json',_GET_response_status),
	'/commands': ('json', _GET_response_commands),
}

def _GET_response(path, args):
	try:
		args = dict(arg.split("=") for arg in args.upper().split("&")) if args is not None else None
		response = GET_paths.get(path, GET_paths.get('/'))
		if callable(response[1]):
			return (response[0], response[1](args))
		return response
	except:
		return ("json", '{"status":"ERROR", "data":"Something goes wrong when generating the response."}')
	

class CustomRequestHandler(BaseHTTPRequestHandler):
	def log_message(self, format, *args):
		if HTTP_LOG_EVERY_REQUEST:
			logging.info("{} - {} - {}".format(self.client_address[0],self.log_date_time_string(), self.path))

	def _set_headers(self, type):
		self.send_response(200)
		if type == 'json':
			self.send_header('Content-type', 'application/json')
		else:
			self.send_header('Content-type', 'text/html')
			
		self.end_headers()

	def do_GET(self):
		path = self.path
		args = None
		if '?' in self.path:
			path, args = path.split('?', 1)
		headers, body = _GET_response(path, args)
		self._set_headers(headers)
		self.wfile.write(body.encode())
		
	def do_POST(self):
		content_length = int(self.headers['Content-Length']) # size of data
		post_data = self.rfile.read(content_length) # data
		self._set_headers()
		self.wfile.write("<html><body><h1>POST!</h1></body></html>".encode())

def start_http():
	server_address = ('', 80)
	httpd = HTTPServer(server_address, CustomRequestHandler)
	logging.info('Starting Web Server...')
	t = Thread(target=httpd.serve_forever)
	t.stop_main = httpd.shutdown
	return t

