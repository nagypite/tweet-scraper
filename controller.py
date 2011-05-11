# -*- coding: utf-8 -*-
import os
import urllib
import re

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import models

def unquote(text):
	def unicode_unquoter(match):
		return unichr(int(match.group(1),16))
	return re.sub(r'%u([0-9a-fA-F]{4})',unicode_unquoter,text)

class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()

		if user:
			self.response.headers['Content-Type'] = 'text/html'

			template_values = {
				'greeting':	'Hello, '+user.nickname(),
				'keywords':	models.listWatchedKeywords(user)
			}

			path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
			self.response.out.write(template.render(path, template_values))

		else:
			self.redirect(users.create_login_url(self.request.uri))
	
class WatchAdd(webapp.RequestHandler):
	def post(self):
		watch = models.UserWatchingKeyword()

		user = users.get_current_user()
		if user:
			watch.user = user
		else:
			self.redirect(users.create_login_url('/'))

		keyword = self.request.get('keyword')
		if len(keyword):
			watch.keyword = keyword
			watch.put()

		self.redirect('/')

class WatchDel(webapp.RequestHandler):
	def get(self, keyid):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url('/'))

		if not len(keyid):
			self.redirect('/')

		key = db.Key(keyid)
		if key:
			db.get(key).delete()

		self.redirect('/')

class Keyword(webapp.RequestHandler):
	def get(self, keyword):
		user = users.get_current_user()
		keyword = unicode(urllib.unquote(keyword), 'utf-8')

		if user:
			template_values = {
				'greeting':	'Hello, '+user.nickname(),
				'keyword':	keyword,
				'tweets':	models.tweetsOnKeyword(keyword)
			}

			if models.userWatchingKeyword(keyword):
				template_file = 'keyword.html'
			else:
				template_file = 'keyword_nowatch.html'

			self.response.headers['Content-Type'] = 'text/html'
			path = os.path.join(os.path.dirname(__file__), 'templates', template_file)
			self.response.out.write(template.render(path, template_values))

		else:
			self.redirect(users.create_login_url(self.request.uri))

application = webapp.WSGIApplication([
						( '/',				MainPage),
						( '/watch',			WatchAdd),
						(r'/keyword/(.*)',	Keyword),
						(r'/unwatch/(.*)',	WatchDel)
			], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
