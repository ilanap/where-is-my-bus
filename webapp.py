import cgi
import os
import webapp2
import json
import logging
import time
import datetime
import jinja2

from urlparse import parse_qs, urlsplit

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch

def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return datetime.datetime.fromtimestamp(int(value)/1000.0).strftime(format)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False)
JINJA_ENVIRONMENT.filters['datetimeformat'] = datetimeformat


if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
	# Production
	REMOTE_URL='https://www.metropoline.com/WS/MeropolineS.svc/SearchOnTime'
else:
	# Local development server
	REMOTE_URL='http://localhost:8080'

class GetMyBus(webapp2.RequestHandler):
	def post(self):
		f= open("static/test.json","r")
		txt = f.read()
		f.close()
		self.response.write(txt)


	def get(self):
		query_params = parse_qs(self.request.query_string)
		bus = None
		if 'bus' in query_params:
			bus = query_params["bus"][0].split(',')

		busstop = query_params["busstop"][0]
		try:
    			form_data = {}
			form_data['Stop_Code'] = busstop
			form_data['isTransportationOfStudents'] = False
    			headers = {'Content-Type': 'application/json'}
			result = urlfetch.fetch(
        			url=REMOTE_URL,
        			payload=json.dumps(form_data),
        			method=urlfetch.POST,
				validate_certificate=True,
        			headers=headers)
			resultObj = json.loads(result.content)
			if bus != None:
				resultObj = [x for x in resultObj if x['lineNumber'] in bus]
		        template_values = {
	        	    'result': resultObj,
	        	    'resultJson': json.dumps(resultObj, indent=4, sort_keys=True),
	        	    'bus': query_params["bus"],
	        	    'busstop': busstop
	       		 }

	        	template = JINJA_ENVIRONMENT.get_template('static/result.template')
	        	self.response.write(template.render(template_values))
		except urlfetch.Error:
			logging.info('Exception')
			logging.exception('Caught exception fetching url')


application = webapp2.WSGIApplication(
	[
	('/', GetMyBus)
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()

