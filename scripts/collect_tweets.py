# Prep
import configparser
from tweepy import Client, Paginator

def twitter_auth(config, keyname = 'bearer'):
	client = Client(config['keys'][keyname], wait_on_rate_limit = True)
	return client

def get_user(user, save_raw = False, start_time = '2016-01-01T00:00:00Z', max_results_per_call = 100):
	exps = ['author_id','referenced_tweets.id','attachments.media_keys','attachments.poll_ids',
			'geo.place_id','entities.mentions.username','referenced_tweets.id.author_id']
	twt_fields = ['attachments','author_id','context_annotations','conversation_id','created_at','entities','geo','in_reply_to_user_id',
				  'lang','possibly_sensitive','public_metrics','referenced_tweets','reply_settings','source']
	usr_fields = ['created_at','description','entities','location','pinned_tweet_id',
				  'profile_image_url','protected','public_metrics','url','verified']
	df = [response for response in Paginator(client.search_all_tweets, 'from:' + str(user), 
											 start_time = start_time, max_results = max_results_per_call, 
											 expansions = exps, tweet_fields = twt_fields, user_fields = usr_fields)]
	return df

# Example code, uncomment to run:
# Reading in configuation
params = configparser.ConfigParser(interpolation = None)
params.read('config.ini')

# Authenticate Twitter API
client = twitter_auth(params, keyn = 'bearer')

# Get user tweets
df = get_user('tedhchen')
