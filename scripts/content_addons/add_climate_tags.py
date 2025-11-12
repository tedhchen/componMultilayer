import configparser, csv
import pandas as pd

# Reading in configuation
params = configparser.ConfigParser()
params.read('config.ini')
params.read(params['path']['root'] + 'scripts\config.ini')

# function to add climate tags
def add_tag(country, update):
	print('Processing ' + country + '...')
	fp = params['data']['componTwitter'] + country + '_edgelist.csv'
	edf = pd.read_csv(fp, dtype = {'id':'str', 'author_id':'str', 'ref_id':'str', 'ref_author_id':'str', 'created_at':'str', 'text':'str', 'type':'str', 'ref_text':'str'})
	climate_tags = pd.read_csv(params['data']['tagLocation'] + '_codes_' + country + '.csv', dtype = {'tw_id': 'str'})
	climate_tags.drop(columns=['text', 'ref_text', 'type'], inplace = True)
	climate_tags.rename(columns = {'tw_id': 'id', 'tag': 'climate'}, inplace = True)
	climate_tags.drop(index = climate_tags[climate_tags.climate < 0].index, inplace = True)
	if update:
		edf.drop(columns=['checked_only95', 'checked_plus95'], inplace = True)
	edf = pd.merge(edf, climate_tags, how = 'left', left_on = 'id', right_on = 'id')
	edf['climate'][edf['climate'].isna()] = 0
	edf['climate'][edf['climate'] > 0] = 1
	edf = edf.astype({'retweet_count': 'Int64', 'reply_count': 'Int64', 'like_count': 'Int64',
					  'quote_count': 'Int64', 'ref_retweet_count': 'Int64', 'ref_reply_count': 'Int64',
					  'ref_like_count': 'Int64', 'ref_quote_count': 'Int64', 'climate': 'Int64'})
	edf.to_csv(fp, index = False, quoting = csv.QUOTE_NONNUMERIC)
	return None

# Running script
countries = ['au', 'br', 'ca', 'cz', 'de', 'fi', 'ie', 'in', 'se']
for country in countries:
	add_tag(country, update = True)
