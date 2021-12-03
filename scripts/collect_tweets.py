# Prep
import configparser, pickle, os
import pandas as pd
from tweepy import Client, Paginator

def twitter_auth(config, keyname = 'bearer'):
	client = Client(config['keys'][keyname], wait_on_rate_limit = True)
	return client

def get_user(user, config, return_df, save_raw, start_time, max_results_per_call = 100):
	exps = ['author_id','referenced_tweets.id','attachments.media_keys','attachments.poll_ids',
			'geo.place_id','entities.mentions.username','referenced_tweets.id.author_id']
	twt_fields = ['attachments','author_id','context_annotations','conversation_id','created_at','entities','geo','in_reply_to_user_id',
				  'lang','possibly_sensitive','public_metrics','referenced_tweets','reply_settings','source']
	usr_fields = ['created_at','description','entities','location','pinned_tweet_id',
				  'profile_image_url','protected','public_metrics','url','verified']
	df = [response for response in Paginator(client.search_all_tweets, 'from:' + str(user), 
											 start_time = start_time, max_results = max_results_per_call, 
											 expansions = exps, tweet_fields = twt_fields, user_fields = usr_fields)]
	if save_raw:
		os.makedirs(config['data']['rawTweets'], exist_ok = True)
		with open(os.path.join(config['data']['rawTweets'], 'apiResponse_' + user + '.pickle'), 'wb') as outpickle:
			pickle.dump(df, outpickle, protocol = 4)
	if return_df:
		return df

def load_accounts(config):
	df = pd.read_csv(os.path.join(config['data']['scratch'], 'all_accounts.csv'), dtype = {'id':'str'}, header = 0)
	accs = list(set(df['id']))
	return accs

def get_accounts(accs, config, ignore_existing = False, start_time = '2017-01-01T00:00:00Z', verbose = True):
	if ignore_existing:
		done = [acc[12:-7] for acc in os.listdir(os.path.join(config['data']['rawTweets']))]
		accs = list(set(accs) - set(done))
		print('Skipping ' + str(len(done)) + ' accounts already collected. ' + str(len(accs)) + ' accounts remaining.')
	for acc in accs:
		if verbose:
			print('Collecting: ' + str(acc) + '.')
		get_user(acc, config = config, return_df = False, save_raw = True, start_time = start_time)
	return None

# Example code, uncomment to run:
# Reading in configuation
params = configparser.ConfigParser(interpolation = None)
params.read('config.ini')

# Authenticate Twitter API
client = twitter_auth(params, keyn = 'bearer')

# Get list of accounts to collect
accounts = load_accounts(config = params)

# Running data collection code
get_accounts(accounts, config = params, ignore_existing = True, start_time = '2017-01-01T00:00:00Z')

# Get user tweets
df = get_user('tedhchen', config = params, save_raw = True)
