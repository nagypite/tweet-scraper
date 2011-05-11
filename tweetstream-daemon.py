import tweetstream

import urllib
import httplib
import time
import threading
import json

USERNAME = "nagypite"
PASSWORD = "qEertzb9"
APP_DOMAIN  = "tweet-scraper.appspot.com:80"
#APP_DOMAIN  = "localhost:8080"
APP_URL  = "/listener"

HTTP_HEADERS = {'X-Its-Me': 'I swear'}
KEYWORDS = []

class ListenerThread(threading.Thread):
	def run(self):
		global runThread, newKeywords
		global USERNAME, PASSWORD, KEYWORDS
		global APP_DOMAIN, APP_URL, HTTP_HEADERS

		time.sleep(10)
		while runThread:
			newKeywords = False

			if len(KEYWORDS) < 1:
				print "ListenerThread: no keywords. sleeping..."
				time.sleep(10)
				continue
			else:
				print "ListenerThread: my new keywords are:", KEYWORDS

			with tweetstream.TrackStream(USERNAME, PASSWORD, KEYWORDS) as stream:
				for tweet in stream:
					if tweet.get('empty', False):
						print "noop", tweet.get('data')
					else:
						to_post = {
							'tweet_id':	tweet.get('id'),
							'tweeter':	tweet.get('user', {}).get('screen_name'),
							'text':		tweet.get('text').encode('utf-8')
						}
						to_post = urllib.urlencode(to_post)

						conn = httplib.HTTPConnection(APP_DOMAIN);
						conn.request("POST", APP_URL, to_post, HTTP_HEADERS)
						response = conn.getresponse()
						print response.status, response.reason, response.read()
						conn.close()

						if newKeywords:
							print "ListenerThread: yay! new keywords!"
							break

						if not runThread:
							break

		print "ListenerThread: stopped"

def main():
	global runThread, newKeywords
	global KEYWORDS

	listener = ListenerThread()
	listener.setName('ListenerThread')
	listener.start()

	old_data = ""

	while runThread:
		print "fetching keyword list..."

		conn = httplib.HTTPConnection(APP_DOMAIN)
		conn.request("GET", APP_URL, None, HTTP_HEADERS)
		response = conn.getresponse()
		print response.status, response.reason

		if response.status == 200:
			data = response.read()

			if data == old_data:
				print "nothing new..."
			else:
				KEYWORDS = [k.encode('utf-8') for k in json.loads(data)]
				print "the new keywords are here:", KEYWORDS
				newKeywords = True
				old_data = data

		else:
			print "communication breakdown"

		try:
			time.sleep(120)

		except KeyboardInterrupt:
			print "\nOK, exiting..."
			runThread = False

if __name__ == "__main__":
	runThread = True
	newKeywors = False
	main()
