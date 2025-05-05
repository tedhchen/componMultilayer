import configparser, csv
import pandas as pd

# Reading in configuation
params = configparser.ConfigParser()
params.read('config.ini')
params.read(params['path']['root'] + 'scripts\config.ini')

# function to add climate tags
def add_tag(country):
	print('Processing ' + country + '...')
	fp = params['data']['componTwitter'] + country + '_edgelist.csv'
	edf = pd.read_csv(fp, dtype = {'id':'str', 'author_id':'str', 'ref_id':'str', 'ref_author_id':'str', 'created_at':'str', 'text':'str', 'type':'str', 'ref_text':'str'})
	climate_tags = pd.read_csv(params['data']['tagLocation'] + 'climate_codes95_' + country + '.csv', dtype = {'tw_id': 'str'})
	climate_tags.rename(columns = {'tw_id': 'id', '95%': 'checked_only95', '95%+all_rest': 'checked_plus95'}, inplace = True)
	edf = pd.merge(edf, climate_tags, how = 'left', left_on = 'id', right_on = 'id')
	edf['checked_only95'][edf['checked_only95'].isna()] = 0
	edf['checked_plus95'][edf['checked_plus95'].isna()] = 0
	edf.to_csv(fp, index = False, quoting = csv.QUOTE_NONNUMERIC)
	return None

# Running script
countries = ['au', 'br', 'ca', 'cz', 'de', 'fi', 'ie', 'se']
for country in countries:
	add_tag(country)
