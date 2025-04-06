# Prep
import configparser, pickle, os, time
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from tweepy import Client, Paginator

# function to authenticate twitter api
def twitter_auth(config, keyname = 'bearer'):
	client = Client(config['keys'][keyname], wait_on_rate_limit = True)
	return client

# function to call API for user's tweets and parse for return
def get_user(user, since_id, config, return_df, save_raw, end_time, max_results_per_call = 5):
	if end_time is None:
		end_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
	exps = ['author_id','referenced_tweets.id','attachments.media_keys','attachments.poll_ids',
			'geo.place_id','entities.mentions.username','referenced_tweets.id.author_id']
	twt_fields = ['attachments','author_id','context_annotations','conversation_id','created_at','entities','geo','in_reply_to_user_id',
				  'lang','possibly_sensitive','public_metrics','referenced_tweets','reply_settings','source']
	usr_fields = ['created_at','description','entities','location','pinned_tweet_id',
				  'profile_image_url','protected','public_metrics','url','verified']
	
	df = client.get_users_tweets(id = str(user), end_time = end_time, max_results = max_results_per_call, since_id = since_id,
								 expansions = exps, tweet_fields = twt_fields, user_fields = usr_fields)
	time.sleep(1.1)
	if df.data is not None:
		print('..' + str(len(df[0])) + ' tweets collected.')
		if save_raw:
			out = extract_essentials(df)
			os.makedirs(config['data']['rawTweets'], exist_ok = True)
			with open(os.path.join(config['data']['rawTweets'], 'apiResponse_' + user + '.pickle'), 'wb') as outpickle:
				pickle.dump(out, outpickle, protocol = 4)
		if return_df:
			return df

# function to parse tweet object returned from API
def extract_essentials(response):
	tweets = [tweet.data for tweet in response.data]
	users = [user.data for user in response.includes.get('users')]
	references = [tweet.data for tweet in response.includes.get('tweets', [])]
	media = [media.data for media in response.includes.get('media', [])]
	return [tweets, users, references, media, response.errors]

# wrapper function for collecting user timelines
def get_accounts(accs, config, end_time, ignore_existing = False, verbose = True, from_latest = False):
	if ignore_existing:
		os.makedirs(config['data']['rawTweets'], exist_ok = True)
		naccs = accs.shape[0]
		done = [acc[12:-7] for acc in os.listdir(os.path.join(config['data']['rawTweets']))]
		if from_latest:
			accs = accs[accs.id > max(list(set(done).intersection(set(accs.id))) + ['0'])]
		else:
			accs = accs[~accs.id.isin(done)]
		print('Skipping ' + str(naccs - accs.shape[0]) + ' accounts already collected. ' + str(accs.shape[0]) + ' accounts remaining.')
	for i, acc in accs.iterrows():
		if verbose:
			print('Collecting: ' + str(acc['id']) + '.')
		get_user(acc['id'], since_id = acc['latest'], config = config, return_df = False, save_raw = True, end_time = end_time)
		if (i + 1) % 50 == 0:
			ptext = '---' + str(i + 1) + ' accounts done.---'
			print('-' * len(ptext) + '\n' + ptext + '\n' + '-' * len(ptext))
	print('Done!')
	return None

# function to call API for list of users' bios and parse for return
def get_bios(acc_ids, config):
	exps = ['affiliation.user_id', 'most_recent_tweet_id', 'pinned_tweet_id']
	twt_fields = ['attachments','author_id','context_annotations','conversation_id','created_at','entities','geo','in_reply_to_user_id',
				  'lang','possibly_sensitive','public_metrics','referenced_tweets','reply_settings','source']
	usr_fields = ['created_at','description','entities','location','pinned_tweet_id',
				  'profile_image_url','protected','public_metrics','url','verified']
	df = client.get_users(ids = list(acc_ids), expansions = exps, tweet_fields = twt_fields, user_fields = usr_fields)
	time.sleep(1.1)
	if df.data is not None:
		users = [user.data for user in df.data]
		tweets = [tweet.data for tweet in df.includes.get('tweets')]
		return [users, tweets]

# wrapper function for collecting user bios
def bio_wrapper(accs, config, name, return_df = False):
	acc_list = np.array_split(accs, -(accs.shape[0] // -100))
	print('Split accounts into ' + str(len(acc_list)) + ' chunks. Collecting...')
	out = []
	i = 0
	for acc_list_sub in acc_list:
		i += 1
		out.append(get_bios(acc_list_sub.id, config))
		print('Chunk ' + str(i) + ' done.')
	out = [[us for chunk in out for us in chunk[0]], [ts for chunk in out for ts in chunk[1]]]
	os.makedirs(config['data']['rawBios'], exist_ok = True)
	with open(os.path.join(config['data']['rawBios'], 'apiBios_' + name + '.pickle'), 'wb') as outpickle:
		pickle.dump(out, outpickle, protocol = 4)
	if return_df:
		return out

# function to load data by country
def load_accounts(config, country):
	df = pd.read_csv(os.path.join(config['data']['recollectLists'], country + '_recollect.csv'), dtype = {'id':'str', 'latest':'str'}, header = 0)
	return df

# # Example code, uncomment to run:
# # Reading in configuation
# params = configparser.ConfigParser(interpolation = None)
# params.read('config.ini')

# # Authenticate Twitter API
# client = twitter_auth(params, keyname = 'bearer')

# countries = ['au', 'br', 'ca', 'cz', 'de', 'fi', 'ie', 'in', 'se']
# for country in countries:
# 	# Get list of accounts to collect
# 	accounts = load_accounts(config = params, country = country)
# 	# Running timeline data collection code
# 	get_accounts(accounts, config = params, end_time = '2025-04-01T00:00:00Z', ignore_existing = True, verbose = True, from_latest = False)
# 	# Running bio data collection code
# 	bio_wrapper(accounts, params, name = country, return_df = True)
