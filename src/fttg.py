#!/usr/bin/env python
# encoding: utf-8

import tweepy
import requests
from datetime import datetime

log = open('../log.txt', 'a')

keys = {
	'TW_CONSUMER_KEY' : 0,
	'TW_CONSUMER_SECRET' : 0,
	'TW_ACCESS_TOKEN' : 0,
	'TW_ACCESS_TOKEN_SECRET' : 0,
	'VK_ACCESS_TOKEN' : 0
}

log.write(datetime.now().strftime("%c") + '\n Reading keys\n')

# Reading keys
with open('../config/.keys') as f_keys:
	i = 0
	for line in f_keys:
		if line[0] != '#' and line[0] != '\n':
			keys[line.split(':')[0]] = line.split(':')[1][:-1]

feeds = []
config = []

log.write(datetime.now().strftime("%c") + '\n Reading config\n')

# Saving config in list
with open('../config/config.conf') as f_conf:
	config = [line.rstrip() for line in f_conf]
	config = list(filter(None, config))

# Twitter part

log.write(datetime.now().strftime("%c") + '\n Reading feeds from config\n')

# Reading feeds from config
for i in range(0, len(config)):
	if config[i] == '[Feeds]':
		j = i + 1
		while config[j][0] != '[':
			feeds.append(config[j])
			j += 1
		break

auth = tweepy.OAuthHandler(keys['TW_CONSUMER_KEY'], keys['TW_CONSUMER_SECRET'])
auth.set_access_token(keys['TW_ACCESS_TOKEN'], keys['TW_ACCESS_TOKEN_SECRET'])
api = tweepy.API(auth)

# don't know what happens when tweeting a pic
def get_latest_tweet(feeds):
	tweets = []
	
	for feed in feeds:
		feed_tweets = api.user_timeline(screen_name = feed)
		
		for tweet in feed_tweets:
			if (tweet.in_reply_to_user_id == None):
				tweets.append(tweet)
				break
	
	most_recent = tweets[0]
	
	for tweet in tweets:
		if tweet.created_at > most_recent.created_at:
			most_recent = tweet
			
	return most_recent.text


log.write(datetime.now().strftime("%c") + \
		'\n Catching the most recent tweet\n')
latest_tweet = get_latest_tweet(feeds)

# VK part

def get_request_url(method, group_id, api_ver, token, parameters = ''):
	if parameters:
		parameters += '&'
	url = 'https://api.vk.com/method/' + method + '?' + parameters + \
								'group_id=' + group_id + '&v' + \
								api_ver + '&access_token=' + token
	return url

group_id = config[config.index("[GroupID]") + 1]
api_ver = config[config.index("[API Version]") + 1]
set_st = 'status.set'
get_st = 'status.get'

log.write(datetime.now().strftime("%c") + \
		'\n Getting current group status\n')
# Get current status
response = requests.get(get_request_url(get_st, group_id, api_ver, \
										keys['VK_ACCESS_TOKEN']))

current_status = response.json()['response']['text']

# If status doesn't match the latest tweet, update it
if current_status != latest_tweet:
	log.write(datetime.now().strftime("%c") + '\n Updating status\n')
	text = 'text=' + latest_tweet
	request = requests.get(get_request_url(set_st, group_id, api_ver, \
										keys['VK_ACCESS_TOKEN'], text))

log.write(datetime.now().strftime("%c") + '\n Exiting from script\n')
