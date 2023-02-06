import configparser, pickle, os, json, csv
import pandas as pd
import numpy as np

def parse_account(responses):
	requireds = ['ref_id', 'author_id_ref', 'text_ref', 'public_metrics.retweet_count_ref', 'public_metrics.reply_count_ref', 'public_metrics.like_count_ref', 'public_metrics.quote_count_ref']
	dfs = []
	for response in responses:
		df = pd.json_normalize(response[0])
		df['type'] = 'original'
		df['ref_id'] = np.nan
		df['ref_text'] = np.nan
		if 'referenced_tweets' in df:
			df.loc[~df['referenced_tweets'].isnull(), 'type'] = [tweet[0].get('type') for tweet in list(df['referenced_tweets']) if tweet is not np.nan]
			df.loc[~df['referenced_tweets'].isnull(), 'ref_id'] = [tweet[0].get('id') for tweet in list(df['referenced_tweets']) if tweet is not np.nan]
			if response[2] != []:
				df = pd.merge(df, pd.json_normalize(response[2]), how = 'left', left_on = 'ref_id', right_on = 'id', suffixes = ('', '_ref'), sort = False)
		kw = {}
		for required in requireds:
			if required not in df:
				kw[required] = np.nan
		if len(kw) > 0:
			df = df.assign(**kw)
		df = df[['id', 'author_id', 'created_at', 'text', 'type', 'public_metrics.retweet_count', 'public_metrics.reply_count', 'public_metrics.like_count', 'public_metrics.quote_count', 'ref_id', 'author_id_ref', 'text_ref', 'public_metrics.retweet_count_ref', 'public_metrics.reply_count_ref', 'public_metrics.like_count_ref', 'public_metrics.quote_count_ref']]
		df.rename(columns = {'public_metrics.retweet_count': 'retweet_count', 'public_metrics.reply_count': 'reply_count', 'public_metrics.like_count': 'like_count', 'public_metrics.quote_count': 'quote_count',
							 'public_metrics.retweet_count_ref': 'ref_retweet_count', 'public_metrics.reply_count_ref': 'ref_reply_count', 'public_metrics.like_count_ref': 'ref_like_count', 'public_metrics.quote_count_ref': 'ref_quote_count',
							 'author_id_ref': 'ref_author_id', 'text_ref': 'ref_text'}, inplace = True)
		df.loc[df['type'] == 'retweeted', ['retweet_count', 'reply_count', 'like_count', 'quote_count']] = np.nan
		dfs.append(df)
		del df
	if dfs != []:
		dfs = pd.concat(dfs)
		dfs.drop_duplicates(subset = 'id', inplace = True)
		dfs.sort_values(by = 'created_at', inplace = True)
		dfs.set_index('id', inplace = True)
		dfs[['retweet_count', 'reply_count', 'like_count', 'quote_count', 'ref_retweet_count', 'ref_reply_count', 'ref_like_count', 'ref_quote_count']] = dfs[['retweet_count', 'reply_count', 'like_count', 'quote_count', 'ref_retweet_count', 'ref_reply_count', 'ref_like_count', 'ref_quote_count']].astype('Int64')
	else:
		dfs = None
	return dfs

def parser_wrapper(config, verbose = True, remove_duplicated = False):
	if not os.path.isfile(config['data']['finalDF']):
		hds = pd.DataFrame(columns = ['author_id', 'created_at', 'text', 'type', 'retweet_count', 'reply_count', 'like_count', 'quote_count', 'ref_id', 'ref_author_id', 'ref_text', 'ref_retweet_count', 'ref_reply_count', 'ref_like_count', 'ref_quote_count'])
		hds.to_csv(config['data']['finalDF'], index_label = 'id')
	files = os.listdir(config['data']['rawTweets'])
	n = 0
	for file in files:
		if verbose:
			print(file)
		with open(os.path.join(config['data']['rawTweets'], file), 'rb') as inpickle:
			tdf = pickle.load(inpickle)
			out = parse_account(tdf)
			n += len(out)
			out.to_csv(config['data']['finalDF'], mode = 'a', header = False, quoting = csv.QUOTE_NONNUMERIC)
		del tdf
	print('Done!', str(n), 'tweet(s) parsed from', str(len(files)), 'account(s).')
	if remove_duplicated:
		print('Removing duplicated entries.')
		df = pd.read_csv(config['data']['finalDF'], dtype = {'id':'str', 'author_id':'str', 
															 'ref_id':'str', 'ref_author_id':'str',
															 'created_at':'str', 'text':'str', 
															 'type':'str', 'ref_text': 'str',
															 'retweet_count':'float64', 'reply_count':'float64', 
															 'like_count':'float64', 'quote_count':'float64', 
															 'ref_retweet_count':'float64', 'ref_reply_count':'float64',
															 'ref_like_count':'float64', 'ref_quote_count':'float64'}, header = 0)
		df.drop_duplicates(subset = ['id', 'created_at'], inplace = True)
		df.sort_values(by = ['author_id', 'created_at', 'id'], inplace = True, ignore_index = True)
		df.to_csv(config['data']['finalDF'], index = False, quoting = csv.QUOTE_NONNUMERIC)
	return None

# # Example code, uncomment to run:
# # Reading in configuation
# params = configparser.ConfigParser(interpolation = None)
# params.read('config.ini')

# # Running parser for the first time
# parser_wrapper(config = params)

# # Running parser after additional data collection
# parser_wrapper(config = params, remove_duplicated = True)
