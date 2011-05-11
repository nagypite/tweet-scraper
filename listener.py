import logging
import time
import urllib
import re

from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import models

def printtime(t):
	return time.strftime('%Y-%m-%d %H:%M:%S', t)

class Listener(webapp.RequestHandler):
	def post(self):
		self.auth()

		logging.info('%s - new tweet from %s' % (printtime(time.gmtime()), self.request.get('tweeter')))

		text = urllib.unquote(self.request.get('text'))

		found = False
		for keyword in models.listWatchedKeywords():
			if text.lower().find(keyword['name']) > -1:
				found = True
				tweet = models.TweetOnKeyword(
										tweetId = self.request.get('tweet_id'),
										tweeter = self.request.get('tweeter'),
										keyword = keyword['name']
									)
				self.response.out.write("FOUND "+keyword['name']+"\n")
				tweet.put()

		if not found:
			self.response.out.write("NOTHING FOUND: "+text+"\n")
	
	def auth(self):
		if not self.request.headers.get('X-Its-Me') == 'I swear':
			self.redirect("/")
	
	def get(self):
#		self.auth()
		self.response.out.write(json.dumps([k['name'] for k in models.listWatchedKeywords()]))

def main():
	logging.getLogger().setLevel(logging.DEBUG)

	application = webapp.WSGIApplication([
							( '/listener',	Listener),
				], debug=True)
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
