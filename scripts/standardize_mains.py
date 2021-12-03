import csv, configparser, os, math
import pandas as pd
import numpy as np
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

# Main function that takes path of data folder and returns a standardized version of the raw account csv
def standardize_mains(path, api, mains = 'main_accounts.csv'):
	df = pd.read_csv(os.path.join(path, mains), dtype = {'username':'str'}, header = 0)
	df['username'] = df['username'].str.lower()
	accs = df['username']
	acc_info = []
	accs_id = [acc for acc in accs if acc.isnumeric()]
	accs_sn = [acc for acc in accs if not acc.isnumeric()]
	if len(accs_id) > 0:
		for set100 in np.array_split(accs_id, math.ceil(len(accs_id)/100)):
			acc_info.extend(api.lookup_users(user_id = list(set100)))
	if len(accs_sn) > 0:
		for set100 in np.array_split(accs_sn, math.ceil(len(accs_sn)/100)):
			acc_info.extend(api.lookup_users(screen_name = list(set100)))
	acc_map = pd.DataFrame([[acc._json['id_str'], acc._json['screen_name'].lower()] for acc in acc_info])
	outdf = pd.merge(df, acc_map, how = 'left', left_on = 'username', right_on = 0)
	outdf = pd.merge(outdf, acc_map, how = 'left', left_on = 'username', right_on = 1)
	outdf.fillna('', inplace = True)
	outdf['sn'] = (outdf['1_x'] + outdf['1_y']).str.lower()
	outdf['id'] = outdf['0_x'] + outdf['0_y']
	outdf.drop_duplicates(inplace = True)
	outdf[outdf['sn'] != ''].to_csv(os.path.join(path, 'main_standardized.csv'), sep = ',', columns = ['org', 'id', 'sn', 'level'], index = False)
	outdf[outdf['sn'] == ''].to_csv(os.path.join(path, 'main_standardized_errors.csv'), sep = ',', columns = ['org', 'username', 'level'], index = False)
	return None

# # Example code, uncomment to run:
# # Reading in configuation
# params = configparser.ConfigParser()
# params.read('config.ini')

# # Twitter authentication
# api = twitter_auth(params)

# # Create a standardized main account list csv file
# standardize_mains(path = params['data']['scratch'], api = api)
