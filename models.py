###
# models.py
###

import urllib

from google.appengine.ext import db
from google.appengine.api import users

###
#
# TweetOnKeyword model
#
###

class TweetOnKeyword(db.Model):
	keyword	= db.StringProperty()
	date	= db.DateTimeProperty(auto_now_add=True)
	tweetId	= db.StringProperty()
	tweeter = db.StringProperty()

def tweetsOnKeyword(keyword):
	q = TweetOnKeyword.all()
	q.filter("keyword =", keyword)

	tweets = []
	for tweet in q:
		tweets.append(tweet)
	
	return tweets

###
#
# UserWatchingKeyword MODEL
#
###

class UserWatchingKeyword(db.Model):
	user	= db.UserProperty()
	keyword	= db.StringProperty()
	date	= db.DateTimeProperty(auto_now_add=True)

def userWatchingKeyword(keyword):
	return UserWatchingKeyword \
				.gql("WHERE user = :user AND keyword = :keyword" \
					, user = users.get_current_user() \
					, keyword = keyword) \
				.count(1) > 0

def listWatchedKeywords(user=None):
	watches = UserWatchingKeyword.all()
<<<<<<< HEAD
	if False and user: ## demo
=======
	if user:
>>>>>>> bb062883a08d8fc446064df7a8fab00a29a694b1
		watches.filter("user =", user)
	watches.order('-date')

	keywords = []
	kws = []
	for w in watches:
		if w.keyword in kws:
			continue
		else:
			kws.append(w.keyword)

		keywords.append({
			'key':		w.key(),
			'name':		w.keyword,
			'escaped':	urllib.quote(w.keyword.encode('utf-8'))
		})

	return keywords

