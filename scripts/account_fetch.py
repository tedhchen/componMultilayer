# Prep
import json, configparser, pickle, csv
import math
import numpy as np
from tweepy import AppAuthHandler, API, Cursor

# Reading in configuation
params = configparser.ConfigParser()
params.read('config.ini')

# Functions
# Takes config file and returns authenticated api object
def twitter_auth(config):
	auth = AppAuthHandler(config['keys']['key'], config['keys']['secret'])
	api = API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
	return api

# Takes given Twitter ID and returns intersection or union of its followers and friends
def get_connections(account, union = False, save_raw = False):
	flwrs = []
	frnds = []
	for flwr in Cursor(api.followers_ids, user_id = account).items():
		flwrs.append(flwr)
	for frnd in Cursor(api.friends_ids, user_id = account).items():
		frnds.append(frnd)
	if union == True:
		connections = list(set(flwrs + frnds))
	else:
		connections = list(set(flwrs).intersection(set(frnds)))
	if save_raw:
		with open('raw_' + account + '.pickle', 'wb') as outpickle:
			pickle.dump([frnds, flwrs], outpickle, protocol = 4)
	return connections

# Checks if any of a set of keywords appears in a user object's bio
def check_user(user, keywords):
	bio = user._json['description'].lower()
	bio_out = '"' + user._json['description'].replace('"', '""') + '"'
	for keyword in keywords:
		match = keyword in bio
		if match:
			break
	if match:
		return [user._json['id_str'], user._json['screen_name'], bio_out]

# Takes a list of Twitter IDs and returns only those whose bios contain at least one specified keyword
# Output is in [('id_str', 'screen_name'), ...] format
def filter_connections(connections, keywords):
	filtered = []
	for set100 in np.array_split(connections, math.ceil(len(connections)/100)):
		filtered.extend(api.lookup_users(list(set100)))
	return list(filter(None, [check_user(connection, keywords) for connection in filtered]))

#  Wrapper taking list of [account, [keywords]] lists and writing their results to separate csv files
def process_accounts(acc_info, save_raw = False):
	for account, keywords in acc_info:
		print('Processing ' + account + '.')
		users = get_connections(account, save_raw = save_raw)
		output = filter_connections(users, keywords)
		np.savetxt('check_' + account + '.csv', output, delimiter = ',', fmt = '% s', encoding = 'utf-8')

#
