# Prep
import json, configparser, pickle, csv, os
import math
import numpy as np
import pandas as pd
from tweepy import AppAuthHandler, OAuthHandler, API, Cursor

# Functions
# Takes config file and returns authenticated api object
def twitter_auth(config, user_auth = False):
	if user_auth:
		auth = OAuthHandler(config['keys']['key'], config['keys']['secret'])
		auth.set_access_token(config['keys']['access'], config['keys']['accesssecret'])
	else:
		auth = AppAuthHandler(config['keys']['key'], config['keys']['secret'])
	api = API(auth, wait_on_rate_limit = True)
	return api

# Takes given Twitter ID and returns intersection or union of its followers and friends
def get_connections(account, config, api, union = False, save_raw = False):
	flwrs = []
	frnds = []
	if account.isnumeric():
		for flwr in Cursor(api.get_follower_ids, user_id = account).items():
			flwrs.append(flwr)
		for frnd in Cursor(api.get_friend_ids, user_id = account).items():
			frnds.append(frnd)
	else:
		for flwr in Cursor(api.get_follower_ids, screen_name = account).items():
			flwrs.append(flwr)
		for frnd in Cursor(api.get_friend_ids, screen_name = account).items():
			frnds.append(frnd)
	if union == True:
		connections = list(set(flwrs + frnds))
	else:
		connections = list(set(flwrs).intersection(set(frnds)))
	if save_raw:
		with open(os.path.join(config['data']['data'], 'raw_' + account + '.pickle'), 'wb') as outpickle:
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
		return [user._json['id_str'], user._json['screen_name'].lower(), bio_out]

# Takes a list of Twitter IDs and returns only those whose bios contain at least one specified keyword
# Output is in [('id_str', 'screen_name'), ...] format
def filter_connections(connections, keywords, api):
	filtered = []
	for set100 in np.array_split(connections, math.ceil(len(connections)/100)):
		filtered.extend(api.lookup_users(user_id = list(set100)))
	return list(filter(None, [check_user(connection, keywords) for connection in filtered]))

#  Wrapper taking list of [account, [keywords]] lists and writing their results to separate csv files
def process_accounts(acc_info, config, api, union = False, save_raw = False):
	for account, keywords in acc_info:
		print('Processing ' + account + '.')
		try:
			users = get_connections(account, config, api, union = union, save_raw = save_raw)
		except:
			users = []
			print(account + ' invalid.')
		if len(users) > 0:
			output = filter_connections(users, keywords, api)
			if len(output) > 0:
				np.savetxt(os.path.join(config['data']['data'], 'check_' + account + '.csv'), output, delimiter = ',', fmt = '% s', encoding = 'utf-8')
	print('Done!')

# Other related utility functions
def get_followers(account, save_raw = False):
	flwrs = []
	for flwr in Cursor(api.followers_ids, user_id = account).items():
		flwrs.append(flwr)
	if save_raw:
		with open('raw_' + account + '.pickle', 'wb') as outpickle:
			pickle.dump(flwrs, outpickle, protocol = 4)
	return flwrs

def read_acc_info(path):
	df = pd.read_csv(path, dtype = {'username':'str', 'level':'int'}, delimiter = ',', encoding = 'utf-8')
	df = df[df['level'] == 0]
	acckeys = []
	for index, line in df.iterrows():
		acckeys.append([line['username'].lower(), line['keywords'].lower().split(', ')])
	return acckeys
	
# # Example code, uncomment to run:
# # Reading in configuation
# params = configparser.ConfigParser()
# params.read('config.ini')

# # Loading accounts of interest and their keyword filters
# # # OPTION 1: Use external file (see structure in template file)
# acc_info = read_acc_info(params['data']['mains'])

# # OPTION 2: For quick testing, just enter the list here.
# # acc_info = [['1397523119770832897', ['postdoctoral', 'scientist']], # Ted's account @tedhchen
# # 			['3254940295', ['political']]] # ECANET's account @ECANETtutkimus

# # Twitter authentication (can be done in some other way if desired)
# api = twitter_auth(params)

# # Processing the list of accounts; will return one csv per account (and raw file in .pickle format)
# process_accounts(acc_info, params, api, save_raw = True) # save_raw = False to not save unfiltered list of followers and friends
